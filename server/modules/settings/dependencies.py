from common.database import get_db
from fastapi import Depends
from modules.relay.dependencies import get_relay_service
from modules.relay.service import RelayService
from modules.settings.repository import SettingsRepository
from modules.settings.service import SettingsService
from sqlalchemy.orm import Session


def get_settings_repository(db: Session = Depends(get_db)) -> SettingsRepository:
    return SettingsRepository(db)


def get_settings_service(
    repository: SettingsRepository = Depends(get_settings_repository),
    relay_service: RelayService = Depends(get_relay_service),
) -> SettingsService:
    return SettingsService(repository, relay_service)
