from common.database import get_db
from fastapi import Depends
from modules.indexers.definitions.service import IndexerDefinitionsService
from sqlalchemy.orm import Session


def get_indexer_definitions_service(
    db: Session = Depends(get_db),
) -> IndexerDefinitionsService:
    return IndexerDefinitionsService()
