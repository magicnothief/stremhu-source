import re

from config import NodeEnv, config
from modules.stremio.constants import (
    ADDON_APP_PREFIX_ID,
    ADDON_STREMHU_PREFIX_ID,
    SEARCH_ID,
)
from modules.stremio.enums import (
    ContentType,
    ExtraName,
    ShortManifestResource,
    StreamIdType,
)
from modules.stremio.schemas import (
    Manifest,
    ManifestBehaviorHints,
    ManifestCatalog,
    ManifestExtra,
    MetaDetail,
    MetaPreview,
    ParsedStreamId,
    StremioStream,
)
from modules.torrent_streams.service import TorrentStreamsService
from modules.users.models import UserModel

# TODO: Az endpoint-ot a setting service-ből kellene olvasni, ha az elkészül.
_HARDCODED_ENDPOINT = "http://localhost:4300"

# Egyszerű semver-kompatibilis regex (major.minor.patch, opcionális pre-release/build metadata eltávolítva)
_SEMVER_PATTERN = re.compile(r"(\d+\.\d+\.\d+)")


def _clean_version(version: str) -> str:
    """Kinyeri a valid semver részt a verzió stringből, vagy '0.0.0'-t ad vissza."""
    match = _SEMVER_PATTERN.search(version)
    return match.group(1) if match else "0.0.0"


from modules.preferences.enums import PreferenceEnum


class StremioService:
    def __init__(self, torrent_streams_service: TorrentStreamsService):
        self.torrent_streams_service = torrent_streams_service

    def manifest(self) -> Manifest:
        """A teljes Stremio addon manifest generálása."""
        version = config.version
        description = config.description

        addon_id = "hu.stremhu-source.addon"
        name = "StremHU Source"

        if config.node_env != NodeEnv.PRODUCTION:
            addon_id = f"{addon_id}.dev"
            name = f"{name} (DEV)"

        valid_version = _clean_version(version)

        catalogs: list[ManifestCatalog] = [
            ManifestCatalog(
                id=SEARCH_ID,
                name="🔍 Torrent - StremHU",
                type=ContentType.MOVIE,
                extra=[ManifestExtra(name=ExtraName.SEARCH, is_required=True)],
            ),
        ]

        return Manifest(
            id=addon_id,
            version=valid_version,
            name=name,
            description=description,
            resources=[
                ShortManifestResource.STREAM,
                ShortManifestResource.CATALOG,
                ShortManifestResource.META,
            ],
            types=[ContentType.MOVIE, ContentType.SERIES],
            id_prefixes=["tt", ADDON_APP_PREFIX_ID, ADDON_STREMHU_PREFIX_ID],
            catalogs=catalogs,
            behavior_hints=ManifestBehaviorHints(
                configurable=True,
                configuration_required=False,
            ),
            logo=f"{_HARDCODED_ENDPOINT}/logo.png",
        )

    # ──────────────────────────────────────────────
    # Streams – éles integráció
    # ──────────────────────────────────────────────

    async def get_streams(
        self,
        user: UserModel,
        parsed_id: ParsedStreamId,
    ) -> list[StremioStream]:
        """Lekéri a lejátszható streameket az adatbázisból vagy indexerekből."""
        if parsed_id.type == StreamIdType.TORRENT:
            # Közvetlen torrent fájl lista lekérdezése
            row_videos = await self.torrent_streams_service.find_by_torrent_id(
                user=user,
                tracker=parsed_id.tracker,
                torrent_id=parsed_id.torrent_id,
            )

            stremio_streams = []
            for video in row_videos:
                stremio_streams.append(
                    self._build_stremio_stream(
                        video=video,
                        tracker_name=video.tracker.name,
                    )
                )
            return stremio_streams

        # IMDb alapú stream lekérdezés kereséssel és feloldással
        torrent_videos, errors = await self.torrent_streams_service.find_by_imdb(
            user=user,
            imdb_id=parsed_id.imdb_id,
            series=parsed_id.series,
        )

        stremio_streams = []
        for video in torrent_videos:
            stremio_streams.append(
                self._build_stremio_stream(
                    video=video,
                    tracker_name=video.tracker.name,
                    seeders=video.seeders,
                )
            )

        return stremio_streams

    def _build_stremio_stream(
        self,
        video,
        tracker_name: str,
        seeders: Optional[int] = None,
    ) -> StremioStream:
        """Egységes segédfüggvény a StremioStream válaszok prémium formázásához."""
        # Csoportosítsuk az attribútumokat kategóriák szerint
        res_attr = next(
            (a for a in video.attributes if a.preference == PreferenceEnum.RESOLUTION),
            None,
        )
        lang_attr = next(
            (a for a in video.attributes if a.preference == PreferenceEnum.LANGUAGE),
            None,
        )
        src_attr = next(
            (a for a in video.attributes if a.preference == PreferenceEnum.SOURCE),
            None,
        )

        video_qualities = [
            a for a in video.attributes if a.preference == PreferenceEnum.VIDEO_QUALITY
        ]
        audio_quality = next(
            (
                a
                for a in video.attributes
                if a.preference == PreferenceEnum.AUDIO_QUALITY
            ),
            None,
        )
        audio_spatial = next(
            (
                a
                for a in video.attributes
                if a.preference == PreferenceEnum.AUDIO_SPATIAL
            ),
            None,
        )

        # Cím sor formázása (pl. "UHD (4K) | MAGYAR | Streaming (WEB-DL)")
        quality_labels = []
        if res_attr:
            quality_labels.append(res_attr.name)
        if lang_attr:
            quality_labels.append(lang_attr.name.upper())
        if src_attr:
            quality_labels.append(src_attr.name)

        title_line = " | ".join(quality_labels)

        # Kép- és hanginformációk (pl. "Dolby Vision, HDR10 / Dolby Digital Plus / Dolby Atmos")
        desc_parts = []
        if video_qualities:
            desc_parts.append(", ".join([vq.name for vq in video_qualities]))
        if audio_quality:
            desc_parts.append(audio_quality.name)
        if audio_spatial:
            desc_parts.append(audio_spatial.name)

        desc_line = " / ".join(desc_parts) if desc_parts else ""

        # Statisztikák (seeders, méret)
        stats_parts = []
        if seeders is not None:
            stats_parts.append(f"👤 {seeders}")
        stats_parts.append(f"📁 {video.file_size}")
        stats_line = " | ".join(stats_parts)

        description = f"{video.file_name}\n"
        if desc_line:
            description += f"✨ {desc_line}\n"
        description += stats_line

        return StremioStream(
            name=f"StremHU\n[{tracker_name}]",
            description=f"{title_line}\n{description}" if title_line else description,
            url=video.play_url,
            behavior_hints={
                "not_web_ready": True,
                "filename": video.file_name,
            },
        )

    def _format_filesize(self, bytes_size: int) -> str:
        if bytes_size == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        import math

        i = int(math.floor(math.log(bytes_size, 1024)))
        p = math.pow(1024, i)
        s = round(bytes_size / p, 2)
        return f"{s} {size_name[i]}"

    # ──────────────────────────────────────────────
    # Catalogs – stub (TODO: TorrentsCacheStore integráció)
    # ──────────────────────────────────────────────

    async def get_metas(self, torrent_id: str) -> list[MetaPreview]:
        """Stub – üres listát ad vissza, amíg a TorrentsCacheStore nincs átportolva."""
        return []

    async def get_meta(self, tracker_id: str, torrent_id: str) -> MetaDetail | None:
        """Stub – None-t ad vissza, amíg a TorrentsCacheStore nincs átportolva."""
        return None
