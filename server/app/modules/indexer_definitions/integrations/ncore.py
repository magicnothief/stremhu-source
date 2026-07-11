"""
@author Sappi <https://github.com/s4pp1/stremhu-source>
@website https://stremhu.hu
"""

from urllib.parse import parse_qs, urljoin, urlparse

import httpx
from selectolax.parser import HTMLParser

from app.modules.indexer_definitions.base_indexer_definition import (
    BaseIndexerDefinition,
)
from app.modules.indexer_definitions.enums import AuthenticationErrorEnum
from app.modules.indexer_definitions.schemas.internal import (
    IndexerDefinitionFindTorrentsResult,
    IndexerDefinitionLogin,
    IndexerDefinitionTorrent,
)
from app.modules.media_attributes.constants import MediaAttributeKey
from app.modules.media_attributes.parser import parse_torrent_name
from app.modules.media_attributes.utils import resolve_attribute_ids


class NcoreIndexerDefinition(BaseIndexerDefinition):
    @property
    def id(self) -> str:
        return "ncore"

    @property
    def name(self) -> str:
        return "nCore"

    @property
    def requires_full_download(self) -> bool:
        return False

    @property
    def url(self) -> str:
        return "https://ncore.pro"

    @property
    def login_path(self) -> str:
        return "/login.php"

    @property
    def details_path(self) -> str:
        return "/torrents.php?action=details&id={torrent_id}"

    def _detect_authentication_error(
        self, response: httpx.Response
    ) -> AuthenticationErrorEnum | None:
        final_path = str(response.url.path)
        original_url = str(response.request.url)
        if response.history:
            original_url = str(response.history[0].url)

        ended_up_at_login = self.login_path in final_path

        if ended_up_at_login:
            if self.login_path in original_url:
                return AuthenticationErrorEnum.CREDENTIAL_ERROR
            return AuthenticationErrorEnum.SESSION_ERROR

        return None

    async def _login(self, credential: IndexerDefinitionLogin) -> httpx.Response:
        return await self._client.post(
            self.login_path,
            data={"nev": credential.username, "pass": credential.password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    async def _fetch_torrents(
        self, imdb_id: str, page: int | None = None
    ) -> IndexerDefinitionFindTorrentsResult:
        current_page = page or 1
        response = await self._client.get(
            "/torrents.php",
            params={
                "oldal": str(current_page),
                "miben": "imdb",
                "mire": imdb_id,
                "miszerint": "seeders",
                "hogyan": "DESC",
                "jsons": True,
            },
        )

        try:
            data = response.json()
        except Exception:
            tree = HTMLParser(response.text)
            error_node = tree.css_first(".lista_mini_error")
            error_text = error_node.text(strip=True) if error_node else None
            if error_text == "Nincs találat!":
                return IndexerDefinitionFindTorrentsResult(torrents=[])
            raise Exception(error_text or "Ismeretlen nCore hiba.")

        torrents: list[IndexerDefinitionTorrent] = []

        for torrent in data.get("results", []):
            category = torrent.get("category", "")
            release_name = torrent.get("release_name", "")
            torrents.append(
                IndexerDefinitionTorrent(
                    imdb_id=torrent.get("imdb_id"),
                    torrent_id=str(torrent["torrent_id"]),
                    seeders=int(torrent.get("seeders", 0)),
                    download_url=torrent["download_url"],
                    attribute_ids=self._resolve_attribute_ids(category, release_name),
                )
            )

        total = int(data.get("total_results", 0))
        limit = int(data.get("perpage", 1)) or 1
        last_page = -(-total // limit)  # math.ceil

        return IndexerDefinitionFindTorrentsResult(
            torrents=torrents,
            next_page=current_page + 1 if current_page < last_page else None,
        )

    async def _fetch_torrent(
        self,
        torrent_id: str,
    ) -> IndexerDefinitionTorrent | None:
        details_url = self.details_path.replace("{torrent_id}", torrent_id)
        response = await self._client.get(details_url)

        tree = HTMLParser(response.text)

        html_node = tree.css_first("html")
        if html_node and "Nem található az adatbázisunkban" in html_node.text():
            return None

        download_node = tree.css_first(
            f'.download a[href*="torrents.php?action=download&id={torrent_id}"]'
        )
        download_path = download_node.attributes.get("href") if download_node else None

        imdb_node = tree.css_first('a[href*="imdb.com/title/"]')
        imdb_anchor_href = imdb_node.attributes.get("href") if imdb_node else None
        imdb_id = (
            imdb_anchor_href.rstrip("/").split("/")[-1] if imdb_anchor_href else None
        )

        if not download_path:
            raise Exception("A letöltési link nem található!")

        return IndexerDefinitionTorrent(
            torrent_id=torrent_id,
            imdb_id=imdb_id,
            download_url=urljoin(self.url, download_path),
        )

    async def _fetch_hit_and_run_ids(self) -> list[str]:
        response = await self._client.get("/hitnrun.php", params={"showall": "false"})
        tree = HTMLParser(response.text)

        content = tree.css_first("#main_tartalom")
        if not content:
            raise Exception("A tartalom nem található.")

        hrefs = [
            node.attributes.get("href")
            for node in content.css('a[href*="torrents.php?action=details&id="]')
        ]

        ids = []
        for href in hrefs:
            if not href:
                continue
            full_url = urljoin(self.url, href)
            id_val = parse_qs(urlparse(full_url).query).get("id", [None])[0]
            if id_val:
                ids.append(id_val)

        return ids

    def _resolve_attribute_ids(self, category: str, release_name: str) -> list[str]:
        """
        Meghatározza egy nCore találat attribútum-azonosítóit (felbontás, nyelv, stb).

        A parse_torrent_name() a tényleges release névből (pl. "...S05.1080p...")
        pontosan kinyeri a felbontást és a nyelv(ek)et is, szemben a régi
        megoldással, ami a nCore kategória-tagből (pl. "hdser_hun") csak egy
        durva "hd" vs. "sd" megkülönböztetést tudott tenni - emiatt minden HD
        kategóriájú találat 720p-nek látszott, még akkor is, ha valójában
        1080p vagy akár 2160p volt.

        A kategória-alapú heurisztikát csak tartalék (external_fallbacks)
        megoldásként adjuk át a parse_torrent_name()-nek: azt csak akkor
        használja fel egy adott kategóriához (pl. felbontás), ha a release
        névben egyáltalán nem talál hozzá egyezést (pl. "Katicabogár...S04" -
        itt a nCore kategória "_hun" végződése az egyetlen nyelvi jelzés).

        Megjegyzés: csak external_fallbacks paramétert használunk (nem
        use_fallbacks-ot), mivel az előbbi mind a GitHub main branch, mind a
        publikált Docker image parse_torrent_name() függvényében elérhető -
        a kettő implementációja @s4pp1/stremhu-source:latest-ben eltér a
        GitHub main branch-től, és nem támogatja a use_fallbacks kwargot.
        """
        category_fallback_ids = [
            self._resolve_resolution_from_category(category),
            self._resolve_language_from_category(category),
        ]
        external_fallbacks = resolve_attribute_ids(category_fallback_ids)

        parsed_attributes = parse_torrent_name(
            release_name, external_fallbacks=external_fallbacks
        )
        return [attribute.id for attribute in parsed_attributes]

    def _resolve_resolution_from_category(self, category: str) -> str:
        if "hd" in category:
            return MediaAttributeKey.R720P
        return MediaAttributeKey.R480P

    def _resolve_language_from_category(self, category: str) -> str:
        if "hun" in category:
            return MediaAttributeKey.HUN
        return MediaAttributeKey.ENG
