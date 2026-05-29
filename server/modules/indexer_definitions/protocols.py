from typing import Protocol

from modules.indexer_accounts.models import IndexerAccountModel


class CredentialsProvider(Protocol):
    def __call__(self, indexer_definition_id: str) -> IndexerAccountModel | None: ...
