import datetime
from typing import NamedTuple

from modules.indexer_definitions.schemas import IndexerDefinition
from modules.relay.schemas import RelayTorrent
from modules.torrents.models import TorrentModel
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TorrentPair(NamedTuple):
    torrent: TorrentModel
    relay: RelayTorrent

    @property
    def info_hash(self) -> str:
        return self.torrent.info_hash


class TorrentState(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    state: int = Field(
        ...,
        description=(
            "checking_files=1, downloading_metadata=2, downloading=3, finished=4, "
            "seeding=5, unused_enum_for_backwards_compatibility_allocating=6, "
            "checking_resume_data=7 "
            "https://www.libtorrent.org/reference-Torrent_Status.html#torrent_status"
        ),
    )
    progress: float


class Torrent(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    info_hash: str
    indexer_definition: IndexerDefinition
    torrent_id: str
    name: str
    download_speed: int
    upload_speed: int
    downloaded: int
    uploaded: int
    total: int
    is_persisted: bool
    full_download: bool | None
    last_played_at: datetime.datetime
    updated_at: datetime.datetime
    created_at: datetime.datetime

    @classmethod
    def from_torrent_pair(
        cls,
        torrent_pair: TorrentPair,
    ) -> "Torrent":
        return cls(
            info_hash=torrent_pair.info_hash,
            indexer_definition=IndexerDefinition.model_validate(
                torrent_pair.torrent.indexer_account.indexer_definition
            ),
            torrent_id=torrent_pair.torrent.torrent_id,
            name=torrent_pair.relay.name,
            download_speed=torrent_pair.relay.download_speed,
            upload_speed=torrent_pair.relay.upload_speed,
            downloaded=torrent_pair.relay.downloaded,
            uploaded=torrent_pair.relay.uploaded,
            total=torrent_pair.relay.total,
            is_persisted=torrent_pair.torrent.is_persisted,
            full_download=torrent_pair.torrent.full_download,
            last_played_at=torrent_pair.torrent.last_played_at,
            updated_at=torrent_pair.torrent.updated_at,
            created_at=torrent_pair.torrent.created_at,
        )


class TorrentCreate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    indexer_id: str
    torrent_id: str


class TorrentUpdate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )

    is_persisted: bool | None = None
    download_full_torrent: bool | None = None
