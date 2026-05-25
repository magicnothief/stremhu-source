import logging

from config import config
from modules.libtorrent_client.service import LibtorrentClientService
from modules.settings.repository import SettingsRepository
from modules.settings.schemas import (
    AppSettings,
    RelaySettings,
    UpdateAppSettings,
    UpdateRelaySettings,
)

logger = logging.getLogger(__name__)

APP_SETTINGS_KEY = "app"
TORRENT_SETTINGS_KEY = "torrent"


class SettingsService:
    def __init__(
        self,
        repository: SettingsRepository,
        libtorrent_client_service: LibtorrentClientService,
    ):
        self.repository = repository
        self.libtorrent_client_service = libtorrent_client_service

    def get_app_settings(self) -> AppSettings:
        record = self.repository.find_one(APP_SETTINGS_KEY)
        data = record.value if record else {}
        return AppSettings.model_validate(data)

    def update_app_settings(self, payload: UpdateAppSettings) -> AppSettings:
        current = self.get_app_settings()
        updated_data = current.model_copy(
            update=payload.model_dump(exclude_unset=True)
        ).model_dump()
        self.repository.create_or_update(APP_SETTINGS_KEY, updated_data)
        return AppSettings.model_validate(updated_data)

    def get_relay_settings(self) -> RelaySettings:
        record = self.repository.find_one(TORRENT_SETTINGS_KEY)
        data = record.value if record else {}
        return RelaySettings.model_validate(data)

    def update_relay_settings(self, payload: UpdateRelaySettings) -> RelaySettings:
        current = self.get_relay_settings()
        updated_data = current.model_copy(
            update=payload.model_dump(exclude_unset=True)
        ).model_dump()
        self.repository.create_or_update(TORRENT_SETTINGS_KEY, updated_data)

        settings = RelaySettings.model_validate(updated_data)
        self._apply_libtorrent_settings(settings)

        return settings

    def initialize_defaults(self):
        """Inicializálja a beállításokat alapértelmezett értékekkel, ha még nem léteznek."""
        logger.info("⚙️ Konfigurációk inicializálása és szinkronizálása...")

        # App Settings
        if not self.repository.find_one(APP_SETTINGS_KEY):
            defaults = AppSettings().model_dump()
            self.repository.create_or_update(APP_SETTINGS_KEY, defaults)

        # Relay Settings
        if not self.repository.find_one(TORRENT_SETTINGS_KEY):
            defaults = RelaySettings(port=config.libtorrent_port).model_dump()
            self.repository.create_or_update(TORRENT_SETTINGS_KEY, defaults)

        # Alkalmazzuk a mentett libtorrent beállításokat induláskor
        settings = self.get_relay_settings()
        self._apply_libtorrent_settings(settings)

    def _apply_libtorrent_settings(self, settings: RelaySettings):
        from modules.libtorrent_client.schemas import (
            UpdateSettings as LibtorrentUpdateSettings,
        )

        libtorrent_update = LibtorrentUpdateSettings(
            download_limit=settings.download_limit,
            upload_limit=settings.upload_limit,
            port=settings.port,
            connections_limit=settings.connections_limit,
            torrent_connections_limit=settings.torrent_connections_limit,
            enable_upnp_and_natpmp=settings.enable_upnp_and_natpmp,
        )
        try:
            self.libtorrent_client_service.update_settings(libtorrent_update)
            logger.info("⚙️ Libtorrent beállítások sikeresen alkalmazva.")
        except Exception as e:
            logger.error(
                f"🚨 Hiba történt a libtorrent beállítások alkalmazása során: {e}"
            )
