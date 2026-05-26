from common.database import get_db
from fastapi import Depends
from modules.attributes.service import AttributesService
from sqlalchemy.orm import Session


def get_attributes_service(
    db: Session = Depends(get_db),
) -> AttributesService:
    return AttributesService(db)
