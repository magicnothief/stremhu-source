from common.database import get_db
from fastapi import Depends
from modules.relay.dependencies import get_relay_service
from modules.settings.repository import SettingsRepository
from modules.settings.service import SettingsService
from sqlalchemy.orm import Session


def create_settings_service(db: Session) -> SettingsService:
    """Hozzárendeli a szervizt egy háttérfeladat vagy HTTP kérés adatbázis munkamenetéhez."""
    repository = SettingsRepository(db)
    relay_service = get_relay_service()
    return SettingsService(repository, relay_service)


def get_settings_service(
    db: Session = Depends(get_db),
) -> SettingsService:
    """FastAPI függőség-injektáló provider a SettingsService példányosításához."""
    return create_settings_service(db)
