from common.database import get_db
from fastapi import Depends
from modules.attributes.repository import AttributesRepository
from modules.attributes.service import AttributesService
from sqlalchemy.orm import Session


def create_attributes_service(db: Session) -> AttributesService:
    repository = AttributesRepository(db)
    return AttributesService(repository)


def get_attributes_service(
    db: Session = Depends(get_db),
) -> AttributesService:
    return create_attributes_service(db)
