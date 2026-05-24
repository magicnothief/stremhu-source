from common.database import get_db
from fastapi import Depends
from modules.libtorrent_client.dependencies import get_libtorrent_client_service
from modules.libtorrent_client.service import LibtorrentClientService
from modules.settings.repository import SettingsRepository
from modules.settings.service import SettingsService
from sqlalchemy.orm import Session


def get_settings_repository(db: Session = Depends(get_db)) -> SettingsRepository:
    return SettingsRepository(db)


def get_settings_service(
    repository: SettingsRepository = Depends(get_settings_repository),
    libtorrent_client_service: LibtorrentClientService = Depends(
        get_libtorrent_client_service
    ),
) -> SettingsService:
    return SettingsService(repository, libtorrent_client_service)
