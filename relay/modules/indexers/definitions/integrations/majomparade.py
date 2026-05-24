from typing import Optional
from urllib.parse import urljoin

import httpx
from modules.attributes.enums import LanguageEnum, ResolutionEnum
from modules.indexers.definitions.base_indexer_definition import BaseIndexerDefinition
from modules.indexers.definitions.enums import AuthenticationErrorEnum
from modules.indexers.definitions.schemas import (
    AdapterLoginRequest,
    AdapterTorrent,
    AdapterTorrentWithInfo,
    FindTorrentsResult,
)
from selectolax.parser import HTMLParser

_CATEGORY_MAP: dict[str, str] = {
    "6": "movie_cam_hun",
    "5": "movie_cam",
    "14": "movie_sd_hun",
    "13": "movie_sd",
    "12": "movie_hd_hun",
    "11": "movie_hd",
    "18": "series_sd_hun",
    "17": "series_sd",
    "19": "series_hd_hun",
    "20": "series_hd",
}

_DOWNLOAD_URL_PREFIX = "/download/"
_CATEGORY_URL_PREFIX = "/torrents/?action=search&categories[]="


class MajomparadeIndexerDefinition(BaseIndexerDefinition):
    @property
    def id(self) -> str:
        return "majomparade"

    @property
    def name(self) -> str:
        return "Majomparádé"

    @property
    def requires_full_download(self) -> bool:
        return True

    @property
    def url(self) -> str:
        return "https://majomparade.eu"

    @property
    def login_path(self) -> str:
        return "/login"

    @property
    def details_path(self) -> str:
        return "/torrent/{torrent_id}"

    def detect_authentication_error(
        self, response: httpx.Response
    ) -> Optional[AuthenticationErrorEnum]:
        original_url = str(response.request.url)

        if self.login_path in original_url and response.request.method == "POST":
            success = None
            try:
                success = response.json().get("success")
            except Exception:
                pass

            if success is False:
                return AuthenticationErrorEnum.CREDENTIAL_ERROR

        final_path = str(response.url.path)
        if self.login_path in final_path:
            return AuthenticationErrorEnum.SESSION_ERROR

        return None

    async def perform_login(self, credential: AdapterLoginRequest) -> httpx.Response:
        return await self._post(
            "/login/",
            data={
                "username": credential.username,
                "password": credential.password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    async def fetch_torrents(
        self, imdb_id: str, page: Optional[int] = None
    ) -> FindTorrentsResult:
        current_page = page or 0
        response = await self._get(
            "/torrents/",
            params={
                "action": "search",
                "search_text": imdb_id,
                "sort": "5",
                "order_by": "0",
                "page": str(current_page),
            },
        )

        html = response.text
        if not isinstance(html, str):
            return FindTorrentsResult(torrents=[])

        tree = HTMLParser(html)
        torrent_rows = tree.css("article.torrent-card")
        torrents: list[AdapterTorrentWithInfo] = []

        for row in torrent_rows:
            cat_node = row.css_first(f'a[href*="{_CATEGORY_URL_PREFIX}"]')
            category_href = cat_node.attributes.get("href") if cat_node else ""
            if not category_href:
                continue
            category = category_href.replace(_CATEGORY_URL_PREFIX, "")

            dl_node = row.css_first(f'a[href*="{_DOWNLOAD_URL_PREFIX}"]')
            download_path = dl_node.attributes.get("href") if dl_node else ""
            if not download_path:
                continue

            torrent_id = str(download_path).replace(_DOWNLOAD_URL_PREFIX, "")
            download_url = urljoin(self.url, download_path)

            imdb_node = row.css_first('a[href*="www.imdb.com/title/"]')
            imdb_url = imdb_node.attributes.get("href") if imdb_node else None
            imdb_parts = imdb_url.rstrip("/").split("/") if imdb_url else []
            imdb_id_val = imdb_parts[-2] if len(imdb_parts) >= 2 else imdb_id

            seed_node = row.css_first(".torrent-card__side .t-stats a")
            seeders_text = seed_node.text(strip=True) if seed_node else ""

            torrents.append(
                AdapterTorrentWithInfo(
                    tracker_id=self.id,
                    torrent_id=torrent_id,
                    download_url=download_url,
                    seeders=int(seeders_text) if seeders_text.isdigit() else 0,
                    imdb_id=imdb_id_val or None,
                    resolution=self._resolve_resolution(category),
                    language=self._resolve_language(category),
                )
            )

        pagination = tree.css_first(".pagination")
        if pagination:
            # eq(-1) direct child:
            child_nodes = [
                n
                for n in pagination.iter()
                if n.tag == "a" or n.tag == "span" or n.tag == "li"
            ]
            next_button = child_nodes[-1] if child_nodes else None
        else:
            next_button = None

        is_disabled = False
        if next_button:
            classes = next_button.attributes.get("class") or ""
            is_disabled = "disabled" in classes

        has_next_page = next_button is not None and not is_disabled

        return FindTorrentsResult(
            torrents=torrents,
            next_page=current_page + 1 if has_next_page else None,
        )

    async def fetch_torrent(self, torrent_id: str) -> AdapterTorrent:
        response = await self._get(f"/torrent/{torrent_id}")
        tree = HTMLParser(response.text)

        dl_node = tree.css_first(f'form[action*="/download/{torrent_id}"]')
        download_path = dl_node.attributes.get("action") if dl_node else None

        imdb_node = tree.css_first('a[href*="www.imdb.com/title/"]')
        imdb_url = imdb_node.attributes.get("href") if imdb_node else None
        imdb_parts = imdb_url.rstrip("/").split("/") if imdb_url else []
        imdb_id = imdb_parts[-2] if len(imdb_parts) >= 2 else None

        if not download_path:
            raise Exception('A "downloadPath" nem található!')

        return AdapterTorrent(
            tracker_id=self.id,
            torrent_id=torrent_id,
            imdb_id=imdb_id,
            download_url=urljoin(self.url, download_path),
        )

    async def fetch_hit_and_run_ids(self) -> list[str]:
        response = await self._get("/hitnrun/")
        tree = HTMLParser(response.text)

        content = tree.css_first("#main-section")
        if not content:
            raise Exception("Az elvárt tartalom nem érhető el.")

        hrefs = [
            node.attributes.get("href")
            for node in content.css('table a[href*="/torrent/"]')
        ]

        return [href.replace("/torrent/", "") for href in hrefs if href]

    # --- Segédfüggvények ---

    def _resolve_resolution(self, category: str) -> ResolutionEnum:
        cat_type = _CATEGORY_MAP.get(category, "none")
        if "hd" in cat_type:
            return ResolutionEnum.R720P
        return ResolutionEnum.R480P

    def _resolve_language(self, category: str) -> LanguageEnum:
        cat_type = _CATEGORY_MAP.get(category, "none")
        if "hun" in cat_type:
            return LanguageEnum.HU
        return LanguageEnum.EN
