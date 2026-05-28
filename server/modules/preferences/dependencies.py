from common.database import get_db
from fastapi import Depends
from modules.attributes.dependencies import get_attributes_service
from modules.attributes.service import AttributesService
from modules.preferences.repository import (
    SystemPreferencesRepository,
    UserPreferencesRepository,
)
from modules.preferences.system_service import SystemPreferencesService
from modules.preferences.user_service import UserPreferencesService
from sqlalchemy.orm import Session


def get_user_preferences_repository(
    db: Session = Depends(get_db),
) -> UserPreferencesRepository:
    """FastAPI dependency provider for UserPreferencesRepository."""
    return UserPreferencesRepository(db)


def get_user_preferences_service(
    repository: UserPreferencesRepository = Depends(get_user_preferences_repository),
    attributes_service: AttributesService = Depends(get_attributes_service),
) -> UserPreferencesService:
    """FastAPI dependency provider for UserPreferencesService."""
    return UserPreferencesService(repository, attributes_service)


def get_system_preferences_repository(
    db: Session = Depends(get_db),
) -> SystemPreferencesRepository:
    """FastAPI dependency provider for SystemPreferencesRepository."""
    return SystemPreferencesRepository(db)


def get_system_preferences_service(
    repository: SystemPreferencesRepository = Depends(
        get_system_preferences_repository
    ),
    attributes_service: AttributesService = Depends(get_attributes_service),
) -> SystemPreferencesService:
    """FastAPI dependency provider for SystemPreferencesService."""
    return SystemPreferencesService(repository, attributes_service)
