import datetime

from modules.indexer_accounts.models import IndexerAccountModel
from modules.indexer_definitions.schemas import (
    IndexerDefinitionLogin,
    IndexerDefinitionTorrent,
)
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class IndexerLogin(IndexerDefinitionLogin):
    indexer_id: str


class IndexerTorrent(IndexerDefinitionTorrent):
    indexer_account: IndexerAccountModel
    torrent_id: str


class DownloadedTorrentFile(BaseModel):
    indexer_account: IndexerAccountModel
    torrent_id: str
    torrent_bytes: bytes


class IndexerFindTorrentsResult(BaseModel):
    torrents: list[IndexerTorrent] = []
    next_page: int | None = None


class Indexer(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        from_attributes=True,
    )

    id: str
    username: str
    download_full_torrent: bool
    hit_and_run: bool | None = None
    keep_seed_seconds: int | None = None
    updated_at: datetime.datetime
    created_at: datetime.datetime


class IndexerUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    hit_and_run: bool | None = None
    keep_seed_seconds: int | None = None
    download_full_torrent: bool | None = None


class IndexerCleanupInfo(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    id: str
    keep_seed_seconds: int | None = None
    not_completed_torrent_ids: list[str] | None = None
