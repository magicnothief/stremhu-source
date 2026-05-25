import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple

import httpx
from aiolimiter import AsyncLimiter

# --- Konstansok és Enums ---
FIND_TORRENTS_LIMIT = 100  # Vagy amit a konfigurációdban beállítottál


class AuthenticationErrorEnum(str, Enum):
    SESSION_ERROR = "SESSION_ERROR"
    CREDENTIAL_ERROR = "CREDENTIAL_ERROR"


# --- Egyedi Kivételek (Exceptions) ---
class TrackerException(Exception):
    """Általános tracker hiba."""

    pass


class CredentialsRequiredException(TrackerException):
    """Hiányzó hitelesítési adatok."""

    pass


class AuthenticationException(TrackerException):
    """Hibás felhasználónév vagy jelszó."""

    pass


# --- Az Automata Re-login Interceptor (HTTPX Auth Plugin) ---
class TrackerAuth(httpx.Auth):
    """
    Egyedi HTTPX interceptor, ami minden kérés után ellenőrzi a session lejáratot,
    és ha szükséges, aszinkron módon újra-bejelentkezik.
    """

    def __init__(
        self,
        detect_auth_error_fn: Callable[
            [httpx.Response], Optional[AuthenticationErrorEnum]
        ],
        relogin_fn: Callable[[], Any],
    ):
        self.detect_auth_error = detect_auth_error_fn
        self.relogin = relogin_fn

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        # 1. Kiküldjük az eredeti kérést
        response: httpx.Response = yield request

        # 2. Ellenőrizzük, hogy elszállt-e az autentikáció
        auth_error = self.detect_auth_error(response)

        if auth_error == AuthenticationErrorEnum.CREDENTIAL_ERROR:
            raise AuthenticationException("Hibás hitelesítési adatok a trackeren.")

        if auth_error == AuthenticationErrorEnum.SESSION_ERROR:
            # Ha session hiba van, aszinkron módon elindítjuk az újra-bejelentkezést
            # A httpx szinkron/aszinkron áthidalása miatt ezt egy belső generátor kezeli
            yield request.options.update(
                auth=None
            )  # Kikapcsoljuk az auth-ot a login kérésre

            # Lefuttatjuk a relogin-t
            asyncio.create_task(self.relogin())

            # Újraküldjük az eredeti kérést a friss sütikkel
            yield request


# --- AZ ABSZTRAKT ALAPOSZTÁLY ---
class BaseIndexerIntegration(ABC):
    def __init__(self, credentials_provider: Callable[[str], Any]):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.get_credentials = credentials_provider

        # Állapotok és limiterek
        self.max_concurrent_rate = 5
        self._limiter = AsyncLimiter(max_rate=self.max_concurrent_rate, time_period=1.0)
        self._login_in_progress: Optional[asyncio.Future] = None

        # A HTTPX kliens felépítése (Beépített cookie kezeléssel)
        self.client = httpx.AsyncClient(
            base_url=self.url,
            follow_redirects=True,  # Fontos az átirányításos login csekkoláshoz
            auth=TrackerAuth(self._detect_authentication_error_wrapper, self.relogin),
        )

    # --- Absztrakt tulajdonságok és metódusok (Implementálni kell) ---

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @property
    @abstractmethod
    def login_path(self) -> str:
        pass

    # --- Absztrakt Üzleti Logikák ---

    @abstractmethod
    def detect_authentication_error(
        self, response: httpx.Response
    ) -> Optional[AuthenticationErrorEnum]:
        """Kiszűri és detektálja a hitelesítési vagy munkamenet hibákat."""
        pass

    @abstractmethod
    async def perform_login(self, credential: Dict[str, str]) -> httpx.Response:
        """Végrehajtja a tényleges POST bejelentkezési kérést."""
        pass

    @abstractmethod
    async def fetch_torrents(
        self, imdb_id: str, page: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Optional[int]]:
        """Keresést hajt végre és visszaadja a (torrents, next_page) párost."""
        pass

    @abstractmethod
    async def fetch_torrent(self, torrent_id: str) -> Dict[str, Any]:
        """Lekéri egy konkrét torrent részletes adatait."""
        pass

    @abstractmethod
    async def fetch_hit_and_run_ids(self) -> List[str]:
        """Lekéri a HnR listán lévő torrent ID-kat."""
        pass

    # --- Megvalósított Publikus API ---

    async def login(self, credential: Optional[Dict[str, str]] = None) -> None:
        if not credential:
            tracker_data = await self.get_credentials(self.id)
            if not tracker_data:
                raise CredentialsRequiredException(
                    f"Nem találhatók mentett adatok a(z) {self.name} trackerhez."
                )
            credential = {
                "username": tracker_data.username,
                "password": tracker_data.password,
            }

        # Sütik törlése új bejelentkezés előtt
        self.client.cookies.clear()

        # Sebességkorlátozott bejelentkezés
        async with self._limiter:
            await self.perform_login(credential)

    async def find(self, imdb_id: str) -> List[Dict[str, Any]]:
        accumulator: List[Dict[str, Any]] = []
        return await self._find_all(imdb_id, None, accumulator)

    async def _find_all(
        self, imdb_id: str, page: Optional[int], accumulator: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if len(accumulator) > FIND_TORRENTS_LIMIT:
            return accumulator

        try:
            async with self._limiter:
                torrents, next_page = await self.fetch_torrents(imdb_id, page)

            accumulator.extend(torrents)

            if next_page:
                return await self._find_all(imdb_id, next_page, accumulator)

            # Szűrés az egyező IMDB ID-ra a végén
            return [t for t in accumulator if t.get("imdbId") == imdb_id]
        except Exception as e:
            error_msg = f"Szerkezeti hiba történt a(z) {self.name} lekérdezése közben."
            self.logger.error(error_msg, exc_info=e)
            raise TrackerException(error_msg) from e

    async def find_one(self, torrent_id: str) -> Dict[str, Any]:
        try:
            async with self._limiter:
                return await self.fetch_torrent(torrent_id)
        except Exception as e:
            error_msg = (
                f"Nem sikerült lekérni a torrent adatlapját a(z) {self.name} oldalon."
            )
            self.logger.error(error_msg, exc_info=e)
            raise TrackerException(error_msg) from e

    async def download(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        torrent_id = payload.get("torrentId")
        download_url = payload.get("downloadUrl")

        try:
            async with self._limiter:
                response = await self.client.get(download_url)
                response.raise_for_status()

            return {
                "torrentId": torrent_id,
                "torrentBuffer": response.content,  # Pythonban a .content adja vissza a nyers bájtokat (Buffer)
            }
        except Exception as e:
            self.logger.error(
                f"Hiba a torrent letöltése közben ({self.name}, ID: {torrent_id})",
                exc_info=e,
            )
            raise e

    async def seed_requirement(self) -> List[str]:
        try:
            async with self._limiter:
                return await self.fetch_hit_and_run_ids()
        except Exception as e:
            error_msg = (
                f"Nem sikerült lekérni a Hit'n'Run listát a(z) {self.name} oldalon."
            )
            self.logger.error(error_msg, exc_info=e)
            raise TrackerException(error_msg) from e

    # --- Belső folyamatkezelők ---

    def _detect_authentication_error_wrapper(
        self, response: httpx.Response
    ) -> Optional[AuthenticationErrorEnum]:
        """Segédfüggvény az auth hiba detektáláshoz."""
        return self.detect_authentication_error(response)

    async def relogin(self) -> None:
        """Kezeli a párhuzamos újra-bejelentkezések összevonását (Mutex/Promise lánc megfelelője)."""
        if self._login_in_progress:
            await self._login_in_progress
            return

        # Létrehozunk egy jövőbeli feladatot (Future)
        loop = asyncio.get_running_loop()
        self._login_in_progress = loop.create_future()

        try:
            self.logger.info(
                f"Munkamenet lejárt. Újra-bejelentkezés a(z) {self.name} trackerre..."
            )
            await self.login()
            self._login_in_progress.set_result(None)
        except Exception as e:
            if not self._login_in_progress.done():
                self._login_in_progress.set_exception(e)
            raise e
        finally:
            self._login_in_progress = None

    async def close(self):
        """Lezárja a HTTP hálózati kapcsolatokat (Alkalmazás leállásakor)."""
        await self.client.aclose()
