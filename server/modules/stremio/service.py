from config import NodeEnv, config
from modules.stremio.constants import (
    ADDON_APP_PREFIX_ID,
    SEARCH_ID,
)
from modules.stremio.enums import (
    ContentType,
    ExtraName,
    ShortManifestResource,
)
from modules.stremio.schemas import (
    Manifest,
    ManifestBehaviorHints,
    ManifestCatalog,
    ManifestExtra,
    ParsedStreamId,
    ParsedTorrentStreamId,
    StremioStream,
)
from modules.torrent_streams.service import TorrentStreamsService
from modules.users.models import UserModel

# TODO: Az endpoint-ot a setting service-ből kellene olvasni, ha az elkészül.
_HARDCODED_ENDPOINT = "http://localhost:4300"


class StremioService:
    def __init__(self, torrent_streams_service: TorrentStreamsService):
        self._torrent_streams_service = torrent_streams_service

    def manifest(self) -> Manifest:
        addon_id = "hu.stremhu-source.addon"
        name = "StremHU Source"

        if config.node_env != NodeEnv.PRODUCTION:
            addon_id = f"{addon_id}.dev"
            name = f"{name} (DEV)"

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
            version=config.version,
            name=name,
            description=config.description,
            resources=[
                ShortManifestResource.STREAM,
                ShortManifestResource.CATALOG,
                ShortManifestResource.META,
            ],
            types=[ContentType.MOVIE, ContentType.SERIES],
            id_prefixes=["tt", ADDON_APP_PREFIX_ID],
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
        if isinstance(parsed_id, ParsedTorrentStreamId):
            torrent_stream = await self._torrent_streams_service.find_by_torrent_id(
                indexer_id=parsed_id.indexer_id,
                torrent_id=parsed_id.torrent_id,
            )

            stremio_streams = []
            if torrent_stream:
                stremio_streams.append(
                    StremioStream.from_torrent_stream(
                        torrent_stream=torrent_stream,
                    )
                )
            return stremio_streams

        # IMDb alapú stream lekérdezés kereséssel és feloldással
        torrent_videos, errors = await self._torrent_streams_service.find_by_imdb(
            user=user,
            imdb_id=parsed_id.imdb_id,
            series=parsed_id.series,
        )

        stremio_streams = []
        for video in torrent_videos:
            stremio_streams.append(
                StremioStream.from_torrent_stream(
                    torrent_stream=video,
                )
            )

        return stremio_streams
