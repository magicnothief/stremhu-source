from common.database import get_db
from fastapi import Depends
from modules.indexers.definitions.dependencies import get_indexer_definitions_service
from modules.indexers.definitions.service import IndexerDefinitionsService
from modules.indexers.repository import IndexersRepository
from modules.indexers.service import IndexersService
from sqlalchemy.orm import Session


def _get_indexers_repository(db: Session = Depends(get_db)) -> IndexersRepository:
    return IndexersRepository(db)


def get_indexers_service(
    indexers_repository: IndexersRepository = Depends(_get_indexers_repository),
    indexer_definitions_service: IndexerDefinitionsService = Depends(
        get_indexer_definitions_service
    ),
) -> IndexersService:
    return IndexersService(indexers_repository, indexer_definitions_service)
