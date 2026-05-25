from typing import List, Optional

from modules.attributes.enums import (
    AudioQualityEnum,
    AudioSpatialEnum,
    LanguageEnum,
    ResolutionEnum,
    SourceEnum,
    VideoQualityEnum,
)
from modules.attributes.schemas import Attribute
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TrackerOption(BaseModel):
    id: str
    name: str


class TorrentStream(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    indexer_id: str
    torrent_id: str
    info_hash: str
    torrent_name: str
    file_name: str
    file_size: str
    file_index: int
    play_url: str
    seeders: int | None = 0
    attributes: List[Attribute] = Field(default_factory=list)
    is_persisted_torrent: bool


class RowTorrentVideo(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    tracker: str
    torrent_id: str = Field(..., alias="torrentId")
    seeders: int
    info_hash: str = Field(..., alias="infoHash")
    torrent_name: str = Field(..., alias="torrentName")
    file_name: str = Field(..., alias="fileName")
    file_size: int = Field(..., alias="fileSize")
    file_index: int = Field(..., alias="fileIndex")
    language: LanguageEnum
    resolution: ResolutionEnum
    video_quality: List[VideoQualityEnum] = Field(..., alias="video-quality")
    audio_quality: AudioQualityEnum = Field(..., alias="audio-quality")
    audio_spatial: Optional[AudioSpatialEnum] = Field(None, alias="audio-spatial")
    source: SourceEnum
    is_in_relay: bool = Field(..., alias="isInRelay")
