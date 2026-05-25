from modules.indexers.definitions.schemas import (
    IndexerDefinitionLogin,
    IndexerDefinitionTorrent,
)
from pydantic import BaseModel


class IndexerLogin(IndexerDefinitionLogin):
    indexer_id: str


class IndexerTorrent(IndexerDefinitionTorrent):
    indexer_id: str
    torrent_id: str


class IndexerFindTorrentsResult(BaseModel):
    torrents: list[IndexerTorrent] = []
    next_page: int | None = None
