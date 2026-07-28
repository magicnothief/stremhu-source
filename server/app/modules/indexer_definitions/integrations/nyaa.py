"""
Nyaa.si indexer definíció - angol feliratos anime kiadások (SubsPlease, Erai-raws).

A többi indexerrel ellentétben a Nyaa egy publikus tracker, ami egyáltalán nem
ismeri az IMDb azonosítókat: a kiadások neve az anime romaji címe (pl.
"[SubsPlease] Shingeki no Kyojin - 04 (1080p) [ABCD1234].mkv"). A
BaseIndexerDefinition API viszont kizárólag imdb_id-t ad át a keresésnek, ezért
ez az integráció maga oldja fel az imdb_id -> anime cím megfeleltetést:

  1. Fribb/anime-lists (imdb_id -> AniList/AniDB azonosítók évadonként),
  2. AniList GraphQL (AniList id -> romaji / angol cím + szinonimák),
  3. Cinemeta (tartalék, ha az anime nem szerepel a fenti listában).

A találatokra utólag rákerül a keresett imdb_id, mivel a
BaseIndexerDefinition._find_all() az `imdb_id` egyezés alapján szűr.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
import unicodedata
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from app.config import config
from app.modules.indexer_definitions.base_indexer_definition import (
    BaseIndexerDefinition,
)
from app.modules.indexer_definitions.schemas.internal import (
    AuthError,
    IndexerDefinitionFindTorrentsResult,
    IndexerDefinitionLogin,
    IndexerDefinitionTorrent,
)
from app.modules.media_attributes.constants import MediaAttributeKey

_ANIME_LIST_URL = (
    "https://raw.githubusercontent.com/Fribb/anime-lists/master/anime-list-full.json"
)
_ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"
_CINEMETA_URL = "https://v3-cinemeta.strem.io/meta/{media_type}/{imdb_id}.json"

# Anime - English-translated
_ENGLISH_TRANSLATED_CATEGORY = "1_2"

# A Cinemeta tartalék forrásnál ezekkel döntjük el, hogy anime-e a találat.
_ANIMATION_GENRE = "Animation"
_ANIME_COUNTRY = "Japan"

# A Nyaa "u=" (feltöltő) szűrője pontosan ezekre a kiadókra szűkíti a találatokat.
_RELEASE_GROUPS = ("SubsPlease", "Erai-raws")

_ANIME_LIST_TTL_SECONDS = 7 * 24 * 60 * 60
_TITLES_TTL_SECONDS = 7 * 24 * 60 * 60
_SEARCH_TTL_SECONDS = 10 * 60

# Memóriában tartott gyorsítótár-bejegyzések felső korlátja (IMDb azonosítónként
# egy bejegyzés), hogy hosszú futásidő alatt se nőjön korlátlanul.
_MAX_CACHE_ENTRIES = 512

# Egy kereséshez maximum ennyi torrentet adunk vissza. A Nyaa RSS oldalanként 75
# elemet ad, és a TorrentSourceProvider minden visszaadott torrenthez letölti a
# .torrent fájlt is - ezért érdemes a legfrissebb kiadásokra korlátozni.
_MAX_TORRENTS = 75

# Kereséskor maximum ennyi különböző címváltozattal próbálkozunk kiadónként.
_MAX_SEARCH_QUERIES = 3

# A Nyaa kereső ÉS kapcsolatot használ a szavak között, ezért a hosszú, teljes
# címek gyakran nulla találatot adnak - ennyi szóra rövidítjük a keresést.
_MAX_QUERY_WORDS = 6

_NYAA_NAMESPACE = "{https://nyaa.si/xmlns/nyaa}"

_NON_ALPHANUMERIC_PATTERN = re.compile(r"[^a-z0-9]+")
_GROUP_PREFIX_PATTERN = re.compile(r"^\s*\[[^\]]*\]\s*")
_TORRENT_ID_PATTERN = re.compile(r"/(?:download|view)/(\d+)")
_FILE_EXTENSION_PATTERN = re.compile(r"\.(?:mkv|mp4|avi)$", re.IGNORECASE)

# "<cím> - 04 (1080p)" / "<cím> - 1208v2 [1080p ...]" - a lusta kvantor miatt a
# legelső olyan " - <szám>" határnál vág, ami után tényleg a technikai rész jön,
# így az Erai-raws stílusú, kötőjelet is tartalmazó címek is helyesen bomlanak.
_EPISODE_PATTERN = re.compile(
    r"^(?P<title>.+?)\s+-\s+(?P<episode>\d{1,4}(?:\.\d+)?(?:v\d+)?)\s*(?=[\[(]|$)"
)

# A cím vége, ha nincs epizódszám (batch kiadások, filmek):
# "[SubsPlease] Show (01-12) (1080p) [Batch]" -> "Show"
_TITLE_ONLY_PATTERN = re.compile(r"^(?P<title>[^\[(]+)")

# Évad-jelölők: ezektől a tokenektől jobbra eső részt levágjuk, hogy megkapjuk a
# sorozat "alap" címét (a Nyaa kereső AND kapcsolatot használ a szavak között,
# ezért a túl specifikus cím nulla találatot adna).
_SEASON_MARKER_TOKENS = frozenset(
    {
        "season",
        "seasons",
        "part",
        "cour",
        "final",
        "ii",
        "iii",
        "iv",
        "2nd",
        "3rd",
        "4th",
        "5th",
        "6th",
        "7th",
        "8th",
        "s2",
        "s3",
        "s4",
        "s5",
        "movie",
        "ova",
        "special",
        "specials",
    }
)


@dataclass(frozen=True)
class _AnimeEntry:
    """Egy Fribb/anime-lists bejegyzés (egy anime évad) lényegi mezői."""

    anilist_id: int | None
    entry_type: str | None
    tvdb_season: int | None
    tvdb_episode_offset: int | None


@dataclass(frozen=True)
class _AnimeTitles:
    """
    Egy animéhez tartozó címváltozatok.

    A `primary` a hivatalos romaji és angol címeket tartalmazza (ezekből épülnek
    a Nyaa keresőkifejezések), az `alternative` a szinonimákat - utóbbiak csak a
    találatok szűrésére szolgálnak, keresésre túl általánosak lennének.
    """

    primary: list[str]
    alternative: list[str]

    def __bool__(self) -> bool:
        return bool(self.primary or self.alternative)

    @property
    def all(self) -> list[str]:
        return [*self.primary, *self.alternative]


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float


def _normalize(value: str) -> str:
    """Ékezet- és írásjelmentes, kisbetűs alak az összehasonlításhoz."""
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_only = "".join(char for char in decomposed if not unicodedata.combining(char))
    return _NON_ALPHANUMERIC_PATTERN.sub(" ", ascii_only.lower()).strip()


def _base_title(normalized_title: str) -> str:
    """
    Levágja az évad-jelölőket a normalizált címről.

    "shingeki no kyojin season 3 part 2" -> "shingeki no kyojin"
    "mushoku tensei iii isekai ittara honki dasu" -> "mushoku tensei"
    """
    tokens = normalized_title.split()
    for index, token in enumerate(tokens):
        if index == 0:
            continue
        if token in _SEASON_MARKER_TOKENS:
            candidate = " ".join(tokens[:index])
            if len(candidate) >= 4:
                return candidate
            break
    return normalized_title


def _search_base(title: str) -> str:
    """
    Nyaa keresőkifejezést képez egy hivatalos címből.

    A kettőspont utáni alcímet elhagyjuk ("Mushoku Tensei: Isekai Ittara Honki
    Dasu" -> "mushoku tensei"), majd levágjuk az évad-jelölőket és a maradékot
    néhány szóra rövidítjük.
    """
    head = title.split(":", 1)[0]
    if len(_normalize(head)) < 4:
        head = title

    base = _base_title(_normalize(head))

    return " ".join(base.split()[:_MAX_QUERY_WORDS])


def _is_latin(value: str) -> bool:
    """Kiszűri a nem latin betűs címeket (japán, héber, thai szinonimák)."""
    normalized = _normalize(value)
    return len(normalized.replace(" ", "")) >= 3


def _is_anime_meta(meta: dict[str, Any]) -> bool:
    """
    Anime-e a Cinemeta találat.

    Az anime japán animációs tartalom, ezért mindkét feltételnek teljesülnie
    kell - az önmagában vett "Animation" a nyugati rajzfilmeket is beengedné.
    """
    genres = meta.get("genres") or []
    country = meta.get("country") or ""

    return _ANIMATION_GENRE in genres and _ANIME_COUNTRY in country


def _parse_release_title(release_name: str) -> str:
    """
    Kinyeri a kiadás nevéből a sorozat/film címét.

    "[SubsPlease] Otome Kaijuu Carameliser - 04 (1080p) [BCF5C655].mkv"
        -> "Otome Kaijuu Carameliser"
    "[Erai-raws] Mushoku Tensei III - Isekai Ittara Honki Dasu - 04 [1080p ...]"
        -> "Mushoku Tensei III - Isekai Ittara Honki Dasu"
    "[SubsPlease] Show (01-12) (1080p) [Batch]" -> "Show"
    """
    name = _GROUP_PREFIX_PATTERN.sub("", release_name).strip()

    episode_match = _EPISODE_PATTERN.match(name)
    if episode_match:
        return episode_match.group("title").strip()

    title_match = _TITLE_ONLY_PATTERN.match(name)
    title = title_match.group("title") if title_match else name

    return _FILE_EXTENSION_PATTERN.sub("", title).strip(" -")


class NyaaIndexerDefinition(BaseIndexerDefinition):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Külön kliens a metaadat-szolgáltatókhoz (a self._client base_url-je a Nyaa).
        self._metadata_client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={"User-Agent": "stremhu-source"},
        )

        self._anime_index: dict[str, list[_AnimeEntry]] | None = None
        self._anime_index_expires_at: float = 0.0
        self._anime_index_lock = asyncio.Lock()

        self._titles_cache: dict[str, _CacheEntry] = {}
        self._titles_cache_loaded = False
        self._search_cache: dict[str, _CacheEntry] = {}

    @property
    def id(self) -> str:
        return "nyaa"

    @property
    def name(self) -> str:
        return "Nyaa"

    @property
    def url(self) -> str:
        return "https://nyaa.si"

    @property
    def login_path(self) -> str:
        return "/login"

    @property
    def details_path(self) -> str:
        return "/view/{torrent_id}"

    @property
    def requires_full_download(self) -> bool:
        return False

    @property
    def max_concurrent(self) -> int:
        return 3

    @property
    def supports_hit_and_run(self) -> bool:
        """A Nyaa publikus tracker, nincs Hit'n'Run szabálya."""
        return False

    # --- Hitelesítés (a Nyaa publikus, nem kell bejelentkezés) ---

    def _detect_authentication_error(
        self,
        response: httpx.Response,
    ) -> AuthError:
        """A Nyaa publikus, nincs munkamenet, amit el lehetne veszíteni."""
        return None

    async def _login(
        self,
        credential: IndexerDefinitionLogin,
    ) -> httpx.Response:
        """
        A Nyaa publikus tracker, nincs szükség hitelesítésre.

        Az alkalmazás viszont csak azokat az indexereket kérdezi le, amikhez
        tartozik "fiók", ezért a bejelentkezés itt csak annyit ellenőriz, hogy az
        oldal egyáltalán elérhető-e. Bármilyen felhasználónév/jelszó megfelel.
        """
        return await self._client.get("/")

    async def _fetch_hit_and_run_ids(self) -> list[str]:
        return []

    # --- Keresés ---

    async def _fetch_torrents(
        self, imdb_id: str, page: int | None = None
    ) -> IndexerDefinitionFindTorrentsResult:
        cached = self._get_cached(self._search_cache, imdb_id)
        if cached is not None:
            return IndexerDefinitionFindTorrentsResult(torrents=cached)

        titles = await self._resolve_titles(imdb_id)

        if not titles:
            self.logger.info(
                "A(z) '%s' IMDb azonosítóhoz nem található anime cím, "
                "a Nyaa keresés kimarad.",
                imdb_id,
            )
            self._set_cached(self._search_cache, imdb_id, [], _SEARCH_TTL_SECONDS)
            return IndexerDefinitionFindTorrentsResult(torrents=[])

        normalized_titles = {_normalize(title) for title in titles.all}
        normalized_titles.discard("")

        # Keresésre és illesztésre is csak a hivatalos címekből képzett
        # alapcímeket használjuk, a szinonimák (pl. "SnK") túl általánosak.
        base_titles = [
            base
            for base in dict.fromkeys(_search_base(title) for title in titles.primary)
            if len(base) >= 4
        ]
        queries = (
            base_titles[:_MAX_SEARCH_QUERIES] or sorted(normalized_titles, key=len)[:1]
        )

        results = await asyncio.gather(
            *(
                self._search_release_group(
                    release_group,
                    queries,
                    normalized_titles,
                    base_titles,
                )
                for release_group in _RELEASE_GROUPS
            ),
            return_exceptions=True,
        )

        torrents: list[IndexerDefinitionTorrent] = []
        seen_torrent_ids: set[str] = set()

        for result in results:
            if isinstance(result, BaseException):
                self.logger.warning("⚠️ Nyaa keresési hiba: %s", result)
                continue

            for torrent in result:
                if torrent.torrent_id in seen_torrent_ids:
                    continue

                seen_torrent_ids.add(torrent.torrent_id)
                torrents.append(torrent.model_copy(update={"imdb_id": imdb_id}))

        torrents = torrents[:_MAX_TORRENTS]

        self._set_cached(self._search_cache, imdb_id, torrents, _SEARCH_TTL_SECONDS)

        # A Nyaa RSS a legfrissebb kiadásokat adja vissza, lapozás nélkül
        # dolgozunk (lásd _MAX_TORRENTS).
        return IndexerDefinitionFindTorrentsResult(torrents=torrents)

    async def _fetch_torrent(self, torrent_id: str) -> IndexerDefinitionTorrent | None:
        if not torrent_id.isdigit():
            return None

        # A letöltési link az azonosítóból képezhető, az adatlapból csak azt
        # kell tudni, hogy létezik-e - ehhez elég a fejléc (HEAD).
        response = await self._client.head(f"/view/{torrent_id}")

        if response.status_code != httpx.codes.OK:
            return None

        return IndexerDefinitionTorrent(
            torrent_id=torrent_id,
            download_url=f"{self.url}/download/{torrent_id}.torrent",
            imdb_id=None,
            attribute_ids=[MediaAttributeKey.ENG],
        )

    async def close(self) -> None:
        await super().close()
        await self._metadata_client.aclose()

    # --- Nyaa RSS ---

    async def _search_release_group(
        self,
        release_group: str,
        queries: list[str],
        normalized_titles: set[str],
        base_titles: list[str],
    ) -> list[IndexerDefinitionTorrent]:
        """
        Végigmegy a címváltozatokon, és az első találatot adó kérésnél megáll.

        A címváltozatok ugyanarra az animére mutatnak, ezért ha az első
        (leggyakrabban a romaji) cím már hozott találatot, a többi kérés csak
        ugyanazokat a kiadásokat hozná vissza.
        """
        torrents: list[IndexerDefinitionTorrent] = []

        for query in queries:
            releases = await self._search(query, release_group)

            for release_name, torrent in releases:
                release_title = _normalize(_parse_release_title(release_name))
                if not self._matches(release_title, normalized_titles, base_titles):
                    self.logger.debug(
                        "A(z) '%s' kiadás nem illeszkedik a keresett animére.",
                        release_name,
                    )
                    continue

                torrents.append(torrent)

            if torrents:
                break

        return torrents

    async def _search(
        self, query: str, release_group: str
    ) -> list[tuple[str, IndexerDefinitionTorrent]]:
        response = await self._client.get(
            "/",
            params={
                "page": "rss",
                "q": query,
                "c": _ENGLISH_TRANSLATED_CATEGORY,
                "f": "0",
                "u": release_group,
            },
        )
        response.raise_for_status()

        try:
            root = ElementTree.fromstring(response.text)
        except ElementTree.ParseError as error:
            raise Exception(f"A Nyaa RSS válasza nem értelmezhető: {error}") from error

        releases: list[tuple[str, IndexerDefinitionTorrent]] = []

        for item in root.iter("item"):
            release_name = (item.findtext("title") or "").strip()
            download_url = (item.findtext("link") or "").strip()

            if not release_name or not download_url:
                continue

            torrent_id_match = _TORRENT_ID_PATTERN.search(download_url)
            if not torrent_id_match:
                continue

            category_id = item.findtext(f"{_NYAA_NAMESPACE}categoryId")
            if category_id and category_id != _ENGLISH_TRANSLATED_CATEGORY:
                continue

            seeders_text = item.findtext(f"{_NYAA_NAMESPACE}seeders") or "0"

            releases.append(
                (
                    release_name,
                    IndexerDefinitionTorrent(
                        torrent_id=torrent_id_match.group(1),
                        download_url=download_url,
                        seeders=int(seeders_text) if seeders_text.isdigit() else 0,
                        # A felbontást, forrást és kodeket a kiadás nevéből
                        # parse_torrent_name() olvassa ki; nyelvi jelölés nincs a
                        # nevekben, ezért az "Anime - English-translated"
                        # kategóriából adódó angolt adjuk tartaléknak.
                        attribute_ids=[MediaAttributeKey.ENG],
                    ),
                )
            )

        return releases

    def _matches(
        self,
        release_title: str,
        normalized_titles: set[str],
        base_titles: list[str],
    ) -> bool:
        if not release_title:
            return False

        for title in normalized_titles:
            if release_title == title:
                return True
            if release_title.startswith(f"{title} ") or title.startswith(
                f"{release_title} "
            ):
                return True

        for base in base_titles:
            if len(base) < 4:
                continue
            if release_title == base or release_title.startswith(f"{base} "):
                return True

        return False

    # --- Metaadatok: imdb_id -> anime címek ---

    async def _resolve_titles(self, imdb_id: str) -> _AnimeTitles:
        cached = self._get_cached(self._titles_cache, imdb_id)
        if cached is not None:
            return cached

        self._load_titles_cache_from_disk()

        cached = self._get_cached(self._titles_cache, imdb_id)
        if cached is not None:
            return cached

        titles = _AnimeTitles(primary=[], alternative=[])

        try:
            entries = await self._get_anime_entries(imdb_id)
        except Exception as error:
            self.logger.warning(
                "⚠️ Az anime lista nem érhető el (%s), Cinemeta tartalék használata.",
                error,
            )
            entries = []

        anilist_ids = [
            entry.anilist_id for entry in entries if entry.anilist_id is not None
        ]

        if anilist_ids:
            try:
                titles = await self._fetch_anilist_titles(anilist_ids)
            except Exception as error:
                self.logger.warning("⚠️ Az AniList lekérés sikertelen: %s", error)

        if not titles:
            titles = await self._fetch_cinemeta_titles(imdb_id)

            # A Cinemeta csak az angol címet ismeri, a kiadások viszont romaji
            # néven futnak ("Attack on Titan" -> "Shingeki no Kyojin"), ezért a
            # megerősítetten anime találatot még feloldjuk az AniList-en.
            if titles.primary:
                titles = await self._search_anilist_titles(titles.primary[0]) or titles

        self._set_cached(self._titles_cache, imdb_id, titles, _TITLES_TTL_SECONDS)
        self._save_titles_cache_to_disk()

        return titles

    @property
    def _titles_cache_path(self) -> Path:
        return config.base_data_dir / "cache" / "nyaa_titles.json"

    def _load_titles_cache_from_disk(self) -> None:
        """
        Betölti a lemezre mentett cím-gyorsítótárat (indulás után egyszer).

        Az üres találatokat is megtartjuk: így az élőszereplős tartalmakra
        újraindítás után sem fut le újra a Cinemeta ellenőrzés.
        """
        if self._titles_cache_loaded:
            return

        self._titles_cache_loaded = True

        try:
            path = self._titles_cache_path
            if not path.is_file():
                return

            with path.open(encoding="utf-8") as file:
                stored = json.load(file)

            now = time.time()
            for imdb_id, entry in stored.items():
                expires_at = entry.get("expires_at", 0)
                if expires_at <= now:
                    continue

                self._titles_cache[imdb_id] = _CacheEntry(
                    value=_AnimeTitles(
                        primary=entry.get("primary", []),
                        alternative=entry.get("alternative", []),
                    ),
                    expires_at=expires_at,
                )
        except Exception as error:
            self.logger.warning(
                "⚠️ A cím-gyorsítótár nem olvasható: %s",
                error,
            )

    def _save_titles_cache_to_disk(self) -> None:
        try:
            path = self._titles_cache_path
            path.parent.mkdir(parents=True, exist_ok=True)

            stored = {
                imdb_id: {
                    "primary": entry.value.primary,
                    "alternative": entry.value.alternative,
                    "expires_at": entry.expires_at,
                }
                for imdb_id, entry in self._titles_cache.items()
            }

            temporary_path = path.with_suffix(".tmp")
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(stored, file)
            temporary_path.replace(path)
        except Exception as error:
            self.logger.warning(
                "⚠️ A cím-gyorsítótár mentése sikertelen: %s",
                error,
            )

    async def _get_anime_entries(self, imdb_id: str) -> list[_AnimeEntry]:
        index = await self._get_anime_index()
        return index.get(imdb_id, [])

    async def _get_anime_index(self) -> dict[str, list[_AnimeEntry]]:
        if self._anime_index is not None and time.time() < self._anime_index_expires_at:
            return self._anime_index

        async with self._anime_index_lock:
            if (
                self._anime_index is not None
                and time.time() < self._anime_index_expires_at
            ):
                return self._anime_index

            raw_index = self._load_anime_index_from_disk()

            if raw_index is None:
                raw_index = await self._download_anime_index()
                self._save_anime_index_to_disk(raw_index)

            self._anime_index = {
                imdb_id: [
                    _AnimeEntry(
                        anilist_id=entry.get("anilist_id"),
                        entry_type=entry.get("type"),
                        tvdb_season=entry.get("tvdb_season"),
                        tvdb_episode_offset=entry.get("tvdb_episode_offset"),
                    )
                    for entry in entries
                ]
                for imdb_id, entries in raw_index.items()
            }
            self._anime_index_expires_at = time.time() + _ANIME_LIST_TTL_SECONDS

            self.logger.info(
                "✅ Nyaa anime lista betöltve (%d IMDb azonosító).",
                len(self._anime_index),
            )

            return self._anime_index

    async def _download_anime_index(self) -> dict[str, list[dict[str, Any]]]:
        """
        Letölti a Fribb/anime-lists teljes listáját, és csak az IMDb-vel
        rendelkező bejegyzések szükséges mezőit tartja meg (~8000 anime).
        """
        response = await self._metadata_client.get(_ANIME_LIST_URL, timeout=120.0)
        response.raise_for_status()

        index: dict[str, list[dict[str, Any]]] = {}

        for entry in response.json():
            imdb_ids = entry.get("imdb_id")
            if not imdb_ids:
                continue
            if isinstance(imdb_ids, str):
                imdb_ids = [imdb_ids]

            season = entry.get("season") or {}
            episode_offset = entry.get("episode_offset") or {}

            compact_entry = {
                "anilist_id": entry.get("anilist_id"),
                "type": entry.get("type"),
                "tvdb_season": season.get("tvdb"),
                "tvdb_episode_offset": episode_offset.get("tvdb"),
            }

            for imdb_id in imdb_ids:
                imdb_id = str(imdb_id).strip()
                if imdb_id.startswith("tt"):
                    index.setdefault(imdb_id, []).append(compact_entry)

        return index

    @property
    def _anime_index_path(self) -> Path:
        return config.base_data_dir / "cache" / "nyaa_anime_index.json"

    def _load_anime_index_from_disk(self) -> dict[str, list[dict[str, Any]]] | None:
        path = self._anime_index_path

        try:
            if not path.is_file():
                return None
            if time.time() - path.stat().st_mtime > _ANIME_LIST_TTL_SECONDS:
                return None
            with path.open(encoding="utf-8") as file:
                return json.load(file)
        except Exception as error:
            self.logger.warning(
                "⚠️ A gyorsítótárazott anime lista nem olvasható: %s", error
            )
            return None

    def _save_anime_index_to_disk(self, index: dict[str, list[dict[str, Any]]]) -> None:
        path = self._anime_index_path

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = path.with_suffix(".tmp")
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(index, file)
            temporary_path.replace(path)
        except Exception as error:
            self.logger.warning(
                "⚠️ Az anime lista gyorsítótárazása sikertelen: %s", error
            )

    async def _fetch_anilist_titles(self, anilist_ids: list[int]) -> _AnimeTitles:
        query = """
        query ($ids: [Int]) {
          Page(page: 1, perPage: 50) {
            media(id_in: $ids, type: ANIME) {
              title { romaji english }
              synonyms
            }
          }
        }
        """

        response = await self._metadata_client.post(
            _ANILIST_GRAPHQL_URL,
            json={"query": query, "variables": {"ids": anilist_ids[:50]}},
        )
        response.raise_for_status()

        payload = response.json()
        media_list = (payload.get("data") or {}).get("Page", {}).get("media") or []

        primary: list[str] = []
        alternative: list[str] = []

        for media in media_list:
            title = media.get("title") or {}
            for value in (title.get("romaji"), title.get("english")):
                if value and _is_latin(value):
                    primary.append(value)

            for synonym in media.get("synonyms") or []:
                if synonym and len(synonym) >= 5 and _is_latin(synonym):
                    alternative.append(synonym)

        return _AnimeTitles(
            primary=list(dict.fromkeys(primary)),
            alternative=list(dict.fromkeys(alternative)),
        )

    async def _search_anilist_titles(self, name: str) -> _AnimeTitles | None:
        """
        Név alapján keres az AniList-en, hogy meglegyen a romaji cím is.

        A találatot csak akkor fogadjuk el, ha valamelyik címváltozata pontosan
        egyezik a keresett névvel - az AniList kereső ugyanis hasonló, de más
        animéket is visszaad.
        """
        query = """
        query ($search: String) {
          Page(page: 1, perPage: 5) {
            media(search: $search, type: ANIME) {
              title { romaji english }
              synonyms
            }
          }
        }
        """

        try:
            response = await self._metadata_client.post(
                _ANILIST_GRAPHQL_URL,
                json={"query": query, "variables": {"search": name}},
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as error:
            self.logger.warning("⚠️ Az AniList keresés sikertelen: %s", error)
            return None

        media_list = (payload.get("data") or {}).get("Page", {}).get("media") or []
        normalized_name = _normalize(name)

        for media in media_list:
            title = media.get("title") or {}
            candidates = [
                title.get("romaji"),
                title.get("english"),
                *(media.get("synonyms") or []),
            ]

            if not any(
                candidate and _normalize(candidate) == normalized_name
                for candidate in candidates
            ):
                continue

            primary = [
                value
                for value in (title.get("romaji"), title.get("english"))
                if value and _is_latin(value)
            ]
            alternative = [
                synonym
                for synonym in media.get("synonyms") or []
                if synonym and len(synonym) >= 5 and _is_latin(synonym)
            ]

            return _AnimeTitles(
                primary=list(dict.fromkeys(primary)),
                alternative=list(dict.fromkeys(alternative)),
            )

        return None

    async def _fetch_cinemeta_titles(self, imdb_id: str) -> _AnimeTitles:
        """
        Tartalék címforrás azokhoz az animékhez, amik nincsenek a Fribb listában.

        A Cinemeta minden filmet és sorozatot ismer, ezért a címet csak akkor
        fogadjuk el, ha a találat tényleg anime (japán animációs) - különben
        minden élőszereplős tartalomra is lefutna két felesleges Nyaa keresés.
        """
        for media_type in ("series", "movie"):
            try:
                response = await self._metadata_client.get(
                    _CINEMETA_URL.format(media_type=media_type, imdb_id=imdb_id)
                )
                response.raise_for_status()
                meta = response.json().get("meta") or {}
            except Exception as error:
                self.logger.warning("⚠️ A Cinemeta lekérés sikertelen: %s", error)
                continue

            name = meta.get("name")
            if not name or not _is_latin(name):
                continue

            if not _is_anime_meta(meta):
                self.logger.debug(
                    "A(z) '%s' (%s) nem anime, a Nyaa keresés kimarad.",
                    name,
                    imdb_id,
                )
                return _AnimeTitles(primary=[], alternative=[])

            return _AnimeTitles(primary=[name], alternative=[])

        return _AnimeTitles(primary=[], alternative=[])

    # --- Gyorsítótár ---

    def _get_cached(self, cache: dict[str, _CacheEntry], key: str) -> Any | None:
        entry = cache.get(key)

        if entry is None:
            return None

        if time.time() >= entry.expires_at:
            cache.pop(key, None)
            return None

        return entry.value

    def _set_cached(
        self,
        cache: dict[str, _CacheEntry],
        key: str,
        value: Any,
        ttl_seconds: int,
    ) -> None:
        cache[key] = _CacheEntry(value=value, expires_at=time.time() + ttl_seconds)

        # A gyorsítótár minden lekérdezett IMDb azonosítót megtartana, ezért a
        # legrégebbi (beszúrási sorrendű) bejegyzéseket eldobjuk.
        while len(cache) > _MAX_CACHE_ENTRIES:
            cache.pop(next(iter(cache)))
