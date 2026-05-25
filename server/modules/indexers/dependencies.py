from common.database import get_db
from fastapi import Depends
from modules.indexers.definitions.dependencies import get_indexer_definitions_service
from modules.indexers.definitions.schemas import (
    CredentialsProvider,
    IndexerDefinitionLogin,
)
from modules.indexers.repository import IndexersRepository
from modules.indexers.service import IndexersService
from sqlalchemy.orm import Session


def _get_indexers_repository(
    db: Session = Depends(get_db),
) -> IndexersRepository:
    return IndexersRepository(db)


async def get_credentials_provider(
    indexers_repository: IndexersRepository = Depends(_get_indexers_repository),
) -> CredentialsProvider:
    async def credentials_provider(indexer_id: str) -> IndexerDefinitionLogin | None:
        user = indexers_repository.find_by_id(indexer_id)
        if not user:
            return None
        return IndexerDefinitionLogin(
            username=user.username,
            password=user.password,
        )

    return credentials_provider


def get_indexers_service(
    indexers_repository: IndexersRepository = Depends(_get_indexers_repository),
    credentials_provider: CredentialsProvider = Depends(get_credentials_provider),
) -> IndexersService:
    indexer_definitions_service = get_indexer_definitions_service(credentials_provider)
    return IndexersService(indexers_repository, indexer_definitions_service)
