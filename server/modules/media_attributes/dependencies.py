from common.database import get_db
from fastapi import Depends
from modules.media_attributes.repository import MediaAttributesRepository
from modules.media_attributes.service import MediaAttributesService
from sqlalchemy.orm import Session


def create_media_attributes_service(db: Session) -> MediaAttributesService:
    repository = MediaAttributesRepository(db)
    return MediaAttributesService(repository)


def get_media_attributes_service(
    db: Session = Depends(get_db),
) -> MediaAttributesService:
    return create_media_attributes_service(db)
