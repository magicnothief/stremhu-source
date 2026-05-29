from modules.indexer_definitions.protocols import CredentialsProvider
from modules.indexer_definitions.service import IndexerDefinitionsService


def create_indexer_definitions_service(
    credentials_provider: CredentialsProvider,
) -> IndexerDefinitionsService:
    return IndexerDefinitionsService(credentials_provider)


def get_indexer_definitions_service(
    credentials_provider: CredentialsProvider,
) -> IndexerDefinitionsService:
    return create_indexer_definitions_service(credentials_provider)
