import functools

from common.database import db_session
from modules.indexer_accounts.repository import IndexerAccountsRepository
from modules.indexer_definitions.schemas import IndexerDefinitionLogin
from modules.indexer_definitions.service import IndexerDefinitionsService


def global_credentials_provider(
    indexer_id: str,
) -> IndexerDefinitionLogin | None:
    with db_session() as db:
        repository = IndexerAccountsRepository(db)
        user = repository.find_by_id(indexer_id)
        if not user:
            return None
        return IndexerDefinitionLogin(
            username=user.username,
            password=user.password,
        )


@functools.lru_cache(maxsize=1)
def get_indexer_definitions_service() -> IndexerDefinitionsService:
    return IndexerDefinitionsService(global_credentials_provider)
