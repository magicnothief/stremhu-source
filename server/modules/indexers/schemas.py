from modules.indexers.definitions.schemas import (
    IndexerDefinitionLogin,
    IndexerDefinitionTorrent,
)
from modules.indexers.models import IndexerModel
from pydantic import BaseModel


class IndexerLogin(IndexerDefinitionLogin):
    indexer_id: str


class IndexerTorrent(IndexerDefinitionTorrent):
    indexer: IndexerModel
    torrent_id: str


class DownloadedTorrentFile(BaseModel):
    indexer: IndexerModel
    torrent_id: str
    torrent_bytes: bytes


class IndexerFindTorrentsResult(BaseModel):
    torrents: list[IndexerTorrent] = []
    next_page: int | None = None
