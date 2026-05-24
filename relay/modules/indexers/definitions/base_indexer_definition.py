import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Callable, Optional

import httpx
from modules.indexers.definitions.enums import AuthenticationErrorEnum
from modules.indexers.definitions.exceptions import (
    AuthenticationException,
    CredentialsRequiredException,
    TrackerException,
)
from modules.indexers.definitions.schemas import (
    AdapterLoginRequest,
    AdapterParsedTorrent,
    AdapterTorrent,
    AdapterTorrentWithInfo,
    FindTorrentsResult,
)

# A NestJS FIND_TORRENTS_LIMIT értéke: 300 (adapter.constant.ts)
FIND_TORRENTS_LIMIT = 300

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/141.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
}


class BaseIndexerDefinition(ABC):
    """
    A NestJS BaseIndexerIntegration absztrakt osztály portolása.

    Minden tracker adapter ebből az osztályból öröklődik és implementálja
    az absztrakt metódusokat. A konkurrencia-kezelés asyncio.Semaphore-ral,
    a HTTP klienskezelés httpx.AsyncClient-tel, a HTML parse-olás pyquery-vel
    történik.
    """

    def __init__(self, credentials_provider: Callable) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._get_credentials = credentials_provider

        # Konkurencia-limiter (a NestJS Bottleneck maxConcurrent megfelelője)
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

        # Párhuzamos relogin-ek összevonásához (a NestJS loginInProgress megfelelője)
        self._login_in_progress: Optional[asyncio.Future] = None

        # httpx kliens – cookie-kat automatikusan kezeli
        self.client = httpx.AsyncClient(
            base_url=self.url,
            follow_redirects=True,
            headers=_DEFAULT_HEADERS,
            timeout=20.0,
        )

    # --- Absztrakt tulajdonságok ---

    @property
    @abstractmethod
    def id(self) -> str:
        """A tracker egyedi azonosítója (pl. 'ncore')."""

    @property
    @abstractmethod
    def name(self) -> str:
        """A tracker megjelenített neve (pl. 'nCore')."""

    @property
    @abstractmethod
    def url(self) -> str:
        """A tracker alap URL-je (pl. 'https://ncore.pro')."""

    @property
    @abstractmethod
    def login_path(self) -> str:
        """A bejelentkezési útvonal (pl. '/login.php')."""

    @property
    @abstractmethod
    def details_path(self) -> str:
        """A torrent adatlap útvonala (pl. '/torrents.php?action=details&id={torrent_id}')."""

    @property
    @abstractmethod
    def requires_full_download(self) -> bool:
        """Szükséges-e a teljes .torrent letöltés a seedeléshez."""

    @property
    def max_concurrent(self) -> int:
        """Max egyidejű HTTP kérések száma (a NestJS maxConcurrent megfelelője)."""
        return 5

    # --- Absztrakt üzleti metódusok ---

    @abstractmethod
    def detect_authentication_error(
        self, response: httpx.Response
    ) -> Optional[AuthenticationErrorEnum]:
        """
        Kiszűri és detektálja a hitelesítési vagy munkamenet hibákat az httpx válasz alapján.

        Implementálandó:
        - Ha a kérés a login oldalra irányított és nem oda indítottuk: SESSION_ERROR
        - Ha a bejelentkezés közvetlenül meghiúsult: CREDENTIAL_ERROR
        - Egyéb esetben: None
        """

    @abstractmethod
    async def perform_login(self, credential: AdapterLoginRequest) -> httpx.Response:
        """Végrehajtja a tényleges POST bejelentkezési kérést a tracker felé."""

    @abstractmethod
    async def fetch_torrents(
        self, imdb_id: str, page: Optional[int] = None
    ) -> FindTorrentsResult:
        """
        Keresést hajt végre a trackeren és visszaadja a találatokat.

        Visszatér:
        - torrents: a talált torrentek listája AdapterTorrentWithInfo-ként
        - next_page: a következő oldal száma, ha van; egyébként None
        """

    @abstractmethod
    async def fetch_torrent(self, torrent_id: str) -> AdapterTorrent:
        """Lekéri egy konkrét torrent részletes adatait az azonosítója alapján."""

    @abstractmethod
    async def fetch_hit_and_run_ids(self) -> list[str]:
        """Lekéri a Hit 'n' Run listán lévő torrent azonosítókat."""

    # --- Megvalósított publikus API ---

    async def login(self, credential: Optional[AdapterLoginRequest] = None) -> None:
        """
        A NestJS login() megfelelője.

        Ha nem adunk meg hitelesítési adatot, a credentials_provider-ből olvassa ki.
        """
        if not credential:
            tracker_data = await self._get_credentials(self.id)
            if not tracker_data:
                raise CredentialsRequiredException(
                    f"{self.name} hitelesítési információk nincsenek megadva."
                )
            credential = AdapterLoginRequest(
                username=tracker_data.username,
                password=tracker_data.password,
            )

        # Sütik törlése új bejelentkezés előtt
        self.client.cookies.clear()

        async with self._semaphore:
            await self.perform_login(credential)

    async def find(self, imdb_id: str) -> list[AdapterTorrentWithInfo]:
        """A NestJS find() megfelelője – összegyűjti az összes találatot lapozással."""
        return await self._find_all(imdb_id, None, [])

    async def find_one(self, torrent_id: str) -> AdapterTorrent:
        """A NestJS findOne() megfelelője – lekéri egy torrent adatait."""
        try:
            async with self._semaphore:
                return await self.fetch_torrent(torrent_id)
        except Exception as e:
            error_msg = f"{self.name} nem érhető el vagy megváltozott a struktúrája."
            self.logger.error(error_msg, exc_info=e)
            raise TrackerException(error_msg) from e

    async def download(self, payload: AdapterTorrent) -> AdapterParsedTorrent:
        """A NestJS download() megfelelője – letölti a .torrent fájlt."""
        try:
            async with self._semaphore:
                response = await self.client.get(payload.download_url)
                response.raise_for_status()

            return AdapterParsedTorrent(
                torrent_id=payload.torrent_id,
                torrent_buffer=response.content,
            )
        except Exception as e:
            self.logger.error(
                f'🚨 Hiba történt a(z) "[{self.name}] - {payload.torrent_id}" torrent letöltése közben.',
                exc_info=e,
            )
            raise

    async def seed_requirement(self) -> list[str]:
        """A NestJS seedRequirement() megfelelője – lekéri a Hit 'n' Run listát."""
        try:
            async with self._semaphore:
                return await self.fetch_hit_and_run_ids()
        except Exception as e:
            error_msg = f"{self.name} nem érhető el vagy megváltozott a struktúrája."
            self.logger.error(error_msg, exc_info=e)
            raise TrackerException(error_msg) from e

    # --- Belső HTTP segédmetódusok ---

    async def _get(self, path: str, **kwargs) -> httpx.Response:
        """
        Sebességkorlátozott GET kérés auth-ellenőrzéssel és automatikus session-frissítéssel.
        Az összes fetch_* metódusnak ezt kell használnia self.client.get() helyett.
        """
        return await self._request("GET", path, **kwargs)

    async def _post(self, path: str, **kwargs) -> httpx.Response:
        """
        Sebességkorlátozott POST kérés auth-ellenőrzéssel és automatikus session-frissítéssel.
        Az összes perform_login metódusnak ezt kell használnia self.client.post() helyett.
        """
        return await self._request("POST", path, **kwargs)

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """
        Kérés küldése és autentikáció ellenőrzése.

        A NestJS Axios interceptor + Bottleneck limiter Python megfelelője.
        Ha SESSION_ERROR → relogin + újrapróbálás.
        Ha CREDENTIAL_ERROR → kivétel dobása.
        """
        async with self._semaphore:
            response = await self.client.request(method, path, **kwargs)

        auth_error = self.detect_authentication_error(response)

        if auth_error == AuthenticationErrorEnum.CREDENTIAL_ERROR:
            raise AuthenticationException(
                f"Sikertelen bejelentkezés a(z) {self.name} fiókba."
            )

        if auth_error == AuthenticationErrorEnum.SESSION_ERROR:
            await self.relogin()
            async with self._semaphore:
                response = await self.client.request(method, path, **kwargs)

        return response

    # --- Belső folyamatkezelők ---

    async def _find_all(
        self,
        imdb_id: str,
        page: Optional[int],
        accumulator: list[AdapterTorrentWithInfo],
    ) -> list[AdapterTorrentWithInfo]:
        """Rekurzív lapozó logika – a NestJS findAll() privát metódus portolása."""
        if len(accumulator) > FIND_TORRENTS_LIMIT:
            return accumulator

        try:
            result = await self.fetch_torrents(imdb_id, page)
            accumulator.extend(result.torrents)

            if result.next_page is not None:
                return await self._find_all(imdb_id, result.next_page, accumulator)

            # Szűrés az egyező IMDB ID-ra – a NestJS logikájával azonos
            return [t for t in accumulator if t.imdb_id == imdb_id]
        except Exception as e:
            error_msg = f"{self.name} nem érhető el vagy megváltozott a struktúrája."
            self.logger.error(error_msg, exc_info=e)
            raise TrackerException(error_msg) from e

    async def relogin(self) -> None:
        """
        Kezeli a párhuzamos újra-bejelentkezések összevonását.

        A NestJS relogin() privát metódus portolása – több egyidejű SESSION_ERROR esetén
        csak egyszer fut le a bejelentkezés, a többi kérés megvárja azt.
        """
        if self._login_in_progress is not None:
            await self._login_in_progress
            return

        loop = asyncio.get_running_loop()
        self._login_in_progress = loop.create_future()

        try:
            self.logger.info(f"🔄 {self.name} session frissítése.")
            await self.login()
            self._login_in_progress.set_result(None)
        except Exception as e:
            if not self._login_in_progress.done():
                self._login_in_progress.set_exception(e)
            raise
        finally:
            self._login_in_progress = None

    async def close(self) -> None:
        """Lezárja a HTTP hálózati kapcsolatokat (alkalmazás leállásakor)."""
        await self.client.aclose()
