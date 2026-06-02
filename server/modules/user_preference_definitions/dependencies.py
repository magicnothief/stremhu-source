from common.database import get_db
from fastapi import Depends
from modules.attributes.dependencies import create_attributes_service
from modules.preference_definitions.dependencies import (
    create_preference_definitions_service,
)
from modules.user_preference_definitions.repository import (
    UserPreferenceDefinitionsRepository,
)
from modules.user_preference_definitions.service import UserPreferenceDefinitionsService
from sqlalchemy.orm import Session


def create_user_preference_definitions_service(
    db: Session,
) -> UserPreferenceDefinitionsService:
    user_preference_definitions_repository = UserPreferenceDefinitionsRepository(db)
    preference_definitions_service = create_preference_definitions_service(db)
    attributes_service = create_attributes_service(db)

    return UserPreferenceDefinitionsService(
        user_preference_definitions_repository,
        preference_definitions_service,
        attributes_service,
    )


def get_user_preference_definitions_service(
    db: Session = Depends(get_db),
) -> UserPreferenceDefinitionsService:
    return create_user_preference_definitions_service(db)
