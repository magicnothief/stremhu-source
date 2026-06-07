from __future__ import annotations

from typing import TYPE_CHECKING

import humanize
from common.schemas.internal import ImdbInfo
from modules.attributes.models import AttributeModel
from modules.preferences.constants import PreferenceKey
from modules.stremio.constants import ADDON_APP_PREFIX_ID
from modules.stremio.enums import (
    ContentType,
    ExtraName,
    ManifestConfigType,
    PosterShape,
    ShortManifestResource,
    StreamIdType,
)
from modules.torrent_files.models import TorrentFileModel
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from pydash import compact

if TYPE_CHECKING:
    from modules.torrent_streams.schemas import TorrentStream

# ──────────────────────────────────────────────
# Manifest schemas
# ──────────────────────────────────────────────


class ManifestExtra(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    name: ExtraName
    is_required: bool | None = None
    options: list[str] | None = None
    options_limit: int | None = None


class ManifestCatalog(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    type: ContentType
    id: str
    name: str
    extra: list[ManifestExtra] | None = None


class ManifestBehaviorHints(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    adult: bool | None = None
    p2p: bool | None = None
    configurable: bool | None = None
    configuration_required: bool | None = None


class ManifestConfig(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    key: str
    type: ManifestConfigType
    default: str | None = None
    title: str | None = None
    options: list[str] | None = None
    required: str | None = None


class FullManifestResource(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    name: ShortManifestResource
    types: list[ContentType]
    id_prefixes: list[str] | None = None


class Manifest(BaseModel):
    """Stremio addon manifest - https://stremio.github.io/stremio-addon-guide/"""

    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    id: str
    name: str
    description: str
    version: str
    resources: list[ShortManifestResource | FullManifestResource]
    types: list[ContentType]
    id_prefixes: list[str] | None = None
    catalogs: list[ManifestCatalog]
    addon_catalogs: list[ManifestCatalog] | None = None
    config: list[ManifestConfig] | None = None
    background: str | None = None
    logo: str | None = None
    contact_email: str | None = None
    behavior_hints: ManifestBehaviorHints | None = None


# ──────────────────────────────────────────────
# Stream schemas
# ──────────────────────────────────────────────


class BehaviorHints(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    country_whitelist: list[str] | None = None
    not_web_ready: bool = True
    binge_group: str | None = None
    filename: str | None = None


class StremioStream(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    name: str
    description: str
    url: str
    behavior_hints: BehaviorHints

    @classmethod
    def from_torrent_stream(
        cls,
        torrent_stream: TorrentStream,
    ) -> StremioStream:
        file_size = f"💾 {humanize.naturalsize(torrent_stream.file_size, binary=True)}"
        seeders = f"👥 {torrent_stream.seeders}"
        indexer = f"🧲 {torrent_stream.indexer_account.indexer_definition.name}"

        description_first_line = " | ".join(compact([indexer, seeders, file_size]))

        resolutions = cls._attributes_parser(
            preference_id=PreferenceKey.RESOLUTION,
            attributes=torrent_stream.attributes,
        )

        readable_resolutions = ", ".join(
            [resolution.name for resolution in resolutions]
        )

        audio_qualities = cls._attributes_parser(
            preference_id=PreferenceKey.AUDIO_QUALITY,
            attributes=torrent_stream.attributes,
        )

        readable_audio_qualities = ", ".join(
            [audio_quality.name for audio_quality in audio_qualities]
        )

        video_qualities = cls._attributes_parser(
            preference_id=PreferenceKey.VIDEO_QUALITY,
            attributes=torrent_stream.attributes,
        )

        readable_video_qualities = ", ".join(
            [video_quality.name for video_quality in video_qualities]
        )

        audio_spatials = cls._attributes_parser(
            preference_id=PreferenceKey.AUDIO_SPATIAL,
            attributes=torrent_stream.attributes,
        )

        readable_audio_spatials = ", ".join(
            [audio_spatial.name for audio_spatial in audio_spatials]
        )

        language = cls._attributes_parser(
            preference_id=PreferenceKey.LANGUAGE,
            attributes=torrent_stream.attributes,
        )

        readable_language = ", ".join([language.name for language in language])

        sources = cls._attributes_parser(
            preference_id=PreferenceKey.SOURCE,
            attributes=torrent_stream.attributes,
        )

        readable_source = ", ".join([source.name for source in sources])

        description_second_line = " | ".join(
            compact(
                [readable_language, readable_audio_qualities, readable_audio_spatials]
            )
        )

        name = " | ".join(
            compact([readable_resolutions, readable_video_qualities, readable_source])
        )
        description = "\n".join([description_first_line, description_second_line])
        binge_group = f"{torrent_stream.indexer_account.indexer_definition.id}-{torrent_stream.torrent_id}"

        return cls(
            name=name,
            description=description,
            url=torrent_stream.play_url,
            behavior_hints=BehaviorHints(
                filename=torrent_stream.file_name,
                binge_group=binge_group,
            ),
        )

    @classmethod
    def _attributes_parser(
        cls,
        preference_id: str,
        attributes: list[AttributeModel],
    ) -> list[AttributeModel]:
        return [
            attribute
            for attribute in attributes
            if attribute.preference_id == preference_id
        ]


class StremioStreams(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    streams: list[StremioStream]


# ──────────────────────────────────────────────
# Catalog / Meta schemas
# ──────────────────────────────────────────────


class MetaLink(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    name: str
    category: str
    url: str


class MetaTrailer(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    yt_id: str
    description: str


class MetaVideo(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    id: str
    title: str
    released: str | None = None
    thumbnail: str | None = None
    available: bool | None = None
    episode: int | None = None
    season: int | None = None
    trailer: str | None = None
    overview: str | None = None


class BaseMeta(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    id: str
    imdb_id: str | None = None
    type: ContentType
    name: str
    poster: str | None = None
    poster_shape: PosterShape = PosterShape.REGULAR
    background: str | None = None
    logo: str | None = None
    description: str | None = None
    imdb_rating: str | None = None
    release_info: str | None = None
    genres: list[str] | None = None
    cast: list[str] | None = None
    director: list[str] | None = None
    links: list[MetaLink] | None = None

    @staticmethod
    def build_meta_id(indexer_id: str, torrent_id: str) -> str:
        return f"{ADDON_APP_PREFIX_ID}{indexer_id}:{torrent_id}"


class MetaPreview(BaseMeta):
    @classmethod
    def from_torrent_file(
        cls,
        torrent_file: TorrentFileModel,
    ) -> MetaPreview:
        return cls(
            id=cls.build_meta_id(
                torrent_file.indexer_id,
                torrent_file.torrent_id,
            ),
            type=ContentType.MOVIE,
            name=torrent_file.info.name,
        )


class MetaDetail(BaseMeta):
    released: str | None = None
    year: str | None = None
    trailers: list[MetaTrailer] | None = None
    videos: list[MetaVideo] | None = None
    runtime: str | None = None
    language: str | None = None
    country: str | None = None
    awards: str | None = None
    website: str | None = None
    behavior_hints: MetaDetailBehaviorHints | None = None
    writer: list[str] | None = None

    @classmethod
    def from_torrent_file(
        cls,
        torrent_file: TorrentFileModel,
    ) -> MetaDetail:
        return cls(
            id=cls.build_meta_id(
                torrent_file.indexer_id,
                torrent_file.torrent_id,
            ),
            type=ContentType.MOVIE,
            name=torrent_file.info.name,
        )


class MetaDetailBehaviorHints(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    default_video_id: str | None = None
    has_scheduled_videos: bool | None = None


class StremioCatalogResponse(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    metas: list[MetaPreview]


class MetaResponse(BaseModel):
    meta: MetaDetail | dict


class StremioCache(BaseModel):
    cache_max_age: int | None = None
    stale_revalidate: int | None = None
    stale_error: int | None = None


class ParsedExtra(BaseModel):
    search: str | None = None
    genre: str | None = None
    skip: int | None = None


class ImdbStreamId(ImdbInfo):
    type: StreamIdType = StreamIdType.IMDB


class TorrentStreamId(BaseModel):
    type: StreamIdType = StreamIdType.TORRENT
    indexer_id: str
    torrent_id: str


StreamId = ImdbStreamId | TorrentStreamId


class ParsedCatalogId(BaseModel):
    tracker_id: str = ""
    torrent_id: str = ""
