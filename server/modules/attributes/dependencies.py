from common.database import get_db
from fastapi import Depends
from modules.attributes.repository import AttributesRepository
from modules.attributes.service import AttributesService
from sqlalchemy.orm import Session


def get_attributes_repository(
    db: Session = Depends(get_db),
) -> AttributesRepository:
    return AttributesRepository(db)


def get_attributes_service(
    repository: AttributesRepository = Depends(get_attributes_repository),
) -> AttributesService:
    return AttributesService(repository)
