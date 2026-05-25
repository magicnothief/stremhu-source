from modules.indexers.definitions.schemas import CredentialsProvider
from modules.indexers.definitions.service import IndexerDefinitionsService


def get_indexer_definitions_service(
    credentials_provider: CredentialsProvider = None,
) -> IndexerDefinitionsService:
    return IndexerDefinitionsService(credentials_provider)
