from common.database import get_db
from fastapi import Depends
from modules.indexers.definitions.schemas import IndexerDefinitionLogin
from modules.indexers.definitions.service import IndexerDefinitionsService
from modules.indexers.repository import IndexersRepository
from modules.indexers.service import IndexersService
from sqlalchemy.orm import Session


def create_indexers_service(db: Session) -> IndexersService:
    indexers_repository = IndexersRepository(db)

    async def credentials_provider(indexer_id: str) -> IndexerDefinitionLogin | None:
        user = indexers_repository.find_by_id(indexer_id)
        if not user:
            return None
        return IndexerDefinitionLogin(
            username=user.username,
            password=user.password,
        )

    indexer_definitions_service = IndexerDefinitionsService(credentials_provider)
    return IndexersService(indexers_repository, indexer_definitions_service)


def get_indexers_service(
    db: Session = Depends(get_db),
) -> IndexersService:
    return create_indexers_service(db)
