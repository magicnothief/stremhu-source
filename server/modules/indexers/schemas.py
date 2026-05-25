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


class DownloadedTorrentFile(BaseModel):
    indexer_id: str
    torrent_id: str
    torrent_bytes: bytes


class IndexerFindTorrentsResult(BaseModel):
    torrents: list[IndexerTorrent] = []
    next_page: int | None = None
