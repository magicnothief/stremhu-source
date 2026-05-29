from common.database import get_db
from fastapi import Depends
from modules.attributes.dependencies import create_attributes_service
from modules.preferences.repository import (
    SystemPreferencesRepository,
    UserPreferencesRepository,
)
from modules.preferences.system_service import SystemPreferencesService
from modules.preferences.user_service import UserPreferencesService
from sqlalchemy.orm import Session


def create_user_preferences_service(db: Session) -> UserPreferencesService:
    """Hozzárendeli a szervizt egy háttérfeladat vagy HTTP kérés adatbázis munkamenetéhez."""
    repository = UserPreferencesRepository(db)
    attributes_service = create_attributes_service(db)
    return UserPreferencesService(repository, attributes_service)


def get_user_preferences_service(
    db: Session = Depends(get_db),
) -> UserPreferencesService:
    """FastAPI dependency provider for UserPreferencesService."""
    return create_user_preferences_service(db)


def create_system_preferences_service(db: Session) -> SystemPreferencesService:
    """Hozzárendeli a szervizt egy háttérfeladat vagy HTTP kérés adatbázis munkamenetéhez."""
    repository = SystemPreferencesRepository(db)
    attributes_service = create_attributes_service(db)
    return SystemPreferencesService(repository, attributes_service)


def get_system_preferences_service(
    db: Session = Depends(get_db),
) -> SystemPreferencesService:
    """FastAPI dependency provider for SystemPreferencesService."""
    return create_system_preferences_service(db)
