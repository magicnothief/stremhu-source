import re

from config import NodeEnv, config
from modules.stremio.constants import (
    ADDON_APP_PREFIX_ID,
    ADDON_STREMHU_PREFIX_ID,
    SEARCH_ID,
)
from modules.stremio.enums import ContentType, ExtraName, ShortManifestResource
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
from modules.users.models import UserModel

# TODO: Az endpoint-ot a setting service-ből kellene olvasni, ha az elkészül.
_HARDCODED_ENDPOINT = "http://localhost:4300"

# Egyszerű semver-kompatibilis regex (major.minor.patch, opcionális pre-release/build metadata eltávolítva)
_SEMVER_PATTERN = re.compile(r"(\d+\.\d+\.\d+)")


def _clean_version(version: str) -> str:
    """Kinyeri a valid semver részt a verzió stringből, vagy '0.0.0'-t ad vissza."""
    match = _SEMVER_PATTERN.search(version)
    return match.group(1) if match else "0.0.0"


class StremioService:
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
    # Streams – stub (TODO: TorrentVideosService integráció)
    # ──────────────────────────────────────────────

    async def get_streams(
        self,
        user: UserModel,
        parsed_id: ParsedStreamId,
    ) -> list[StremioStream]:
        """Stub – üres listát ad vissza, amíg a TorrentVideosService nincs átportolva."""
        return []

    # ──────────────────────────────────────────────
    # Catalogs – stub (TODO: TorrentsCacheStore integráció)
    # ──────────────────────────────────────────────

    async def get_metas(self, torrent_id: str) -> list[MetaPreview]:
        """Stub – üres listát ad vissza, amíg a TorrentsCacheStore nincs átportolva."""
        return []

    async def get_meta(self, tracker_id: str, torrent_id: str) -> MetaDetail | None:
        """Stub – None-t ad vissza, amíg a TorrentsCacheStore nincs átportolva."""
        return None
