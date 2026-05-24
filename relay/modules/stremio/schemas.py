from __future__ import annotations

from dataclasses import dataclass

from modules.stremio.enums import (
    ContentType,
    ExtraName,
    ManifestConfigType,
    PosterShape,
    ShortManifestResource,
    StreamIdType,
)
from pydantic import BaseModel, ConfigDict

# ──────────────────────────────────────────────
# Manifest schemas
# ──────────────────────────────────────────────


class ManifestExtra(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: ExtraName
    is_required: bool | None = None
    options: list[str] | None = None
    options_limit: int | None = None


class ManifestCatalog(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: ContentType
    id: str
    name: str
    extra: list[ManifestExtra] | None = None


class ManifestBehaviorHints(BaseModel):
    adult: bool | None = None
    p2p: bool | None = None
    configurable: bool | None = None
    configuration_required: bool | None = None


class ManifestConfig(BaseModel):
    key: str
    type: ManifestConfigType
    default: str | None = None
    title: str | None = None
    options: list[str] | None = None
    required: str | None = None


class FullManifestResource(BaseModel):
    name: ShortManifestResource
    types: list[ContentType]
    id_prefixes: list[str] | None = None


class Manifest(BaseModel):
    """Stremio addon manifest – https://stremio.github.io/stremio-addon-guide/"""

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
    country_whitelist: list[str] | None = None
    not_web_ready: bool
    binge_group: str | None = None
    filename: str | None = None


class StremioStream(BaseModel):
    name: str
    description: str
    url: str
    behavior_hints: BehaviorHints


class StremioStreamsResponse(BaseModel):
    streams: list[StremioStream]


# ──────────────────────────────────────────────
# Catalog / Meta schemas
# ──────────────────────────────────────────────


class MetaLink(BaseModel):
    name: str
    category: str
    url: str


class MetaTrailer(BaseModel):
    yt_id: str
    description: str


class MetaVideo(BaseModel):
    id: str
    title: str
    released: str | None = None
    thumbnail: str | None = None
    available: bool | None = None
    episode: int | None = None
    season: int | None = None
    trailer: str | None = None
    overview: str | None = None


class MetaPreview(BaseModel):
    id: str
    imdb_id: str | None = None
    type: ContentType
    name: str
    poster: str | None = None
    poster_shape: PosterShape | None = None
    background: str | None = None
    logo: str | None = None
    description: str | None = None
    imdb_rating: str | None = None
    release_info: str | None = None
    genres: list[str] | None = None
    cast: list[str] | None = None
    director: list[str] | None = None
    links: list[MetaLink] | None = None


class MetaDetailBehaviorHints(BaseModel):
    default_video_id: str | None = None
    has_scheduled_videos: bool | None = None


class MetaDetail(MetaPreview):
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


class StremioCatalogResponse(BaseModel):
    metas: list[MetaPreview]


class MetaResponse(BaseModel):
    meta: MetaDetail


class StremioCache(BaseModel):
    cache_max_age: int | None = None
    stale_revalidate: int | None = None
    stale_error: int | None = None


# ──────────────────────────────────────────────
# Parsing típusok (internal, nem response DTO)
# ──────────────────────────────────────────────


@dataclass
class ParsedExtra:
    search: str | None = None
    genre: str | None = None
    skip: int | None = None


@dataclass
class ParsedStreamSeries:
    season: int
    episode: int


@dataclass
class ParsedImdbStreamId:
    type: StreamIdType = StreamIdType.IMDB
    imdb_id: str = ""
    series: ParsedStreamSeries | None = None


@dataclass
class ParsedTorrentStreamId:
    type: StreamIdType = StreamIdType.TORRENT
    tracker: str = ""
    torrent_id: str = ""


ParsedStreamId = ParsedImdbStreamId | ParsedTorrentStreamId


@dataclass
class ParsedCatalogId:
    tracker_id: str = ""
    torrent_id: str = ""
