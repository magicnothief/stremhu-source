import datetime

from modules.indexers.definitions.schemas import IndexerDefinition
from modules.persisted_torrents.models import PersistedTorrentModel
from modules.relay.schemas import RelayTorrent
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


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
    def from_entity(
        cls,
        entity: PersistedTorrentModel,
        relay_torrent: RelayTorrent,
    ) -> "Torrent":
        return cls(
            info_hash=entity.info_hash,
            indexer_definition=IndexerDefinition.model_validate(
                entity.indexer.definition
            ),
            torrent_id=entity.torrent_id,
            name=relay_torrent.name,
            download_speed=relay_torrent.download_speed,
            upload_speed=relay_torrent.upload_speed,
            downloaded=relay_torrent.downloaded,
            uploaded=relay_torrent.uploaded,
            total=relay_torrent.total,
            is_persisted=entity.is_persisted,
            full_download=entity.full_download,
            last_played_at=entity.last_played_at,
            updated_at=entity.updated_at,
            created_at=entity.created_at,
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
