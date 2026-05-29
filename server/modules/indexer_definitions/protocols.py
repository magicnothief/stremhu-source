from typing import Protocol

from modules.indexer_definitions.schemas import IndexerDefinitionLogin


class CredentialsProvider(Protocol):
    def __call__(self, indexer_id: str) -> IndexerDefinitionLogin | None: ...
