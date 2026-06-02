from common.database import get_db
from fastapi import Depends
from modules.preferences.repository import PreferencesRepository
from modules.preferences.service import PreferencesService
from sqlalchemy.orm import Session


def create_preferences_service(
    db: Session,
) -> PreferencesService:
    preferences_repository = PreferencesRepository(db)
    return PreferencesService(preferences_repository)


def get_preferences_service(
    db: Session = Depends(get_db),
) -> PreferencesService:
    return create_preferences_service(db)
