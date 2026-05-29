from modules.kodi.schemas import (
    KodiImdbStreamsParams,
)
from modules.stremio.schemas import ParsedStreamSeries
from modules.torrent_streams.schemas import TorrentStream
from modules.torrent_streams.service import TorrentStreamsService
from modules.users.models import UserModel


class KodiService:
    def __init__(self, torrent_streams_service: TorrentStreamsService):
        self._torrent_streams_service = torrent_streams_service

    async def imdb_streams(
        self,
        user: UserModel,
        imdb_id: str,
        payload: KodiImdbStreamsParams | None = None,
    ) -> tuple[list[TorrentStream], list[str]]:
        series: ParsedStreamSeries | None = None
        if payload and payload.season is not None and payload.episode is not None:
            series = ParsedStreamSeries(
                season=payload.season,
                episode=payload.episode,
            )

        torrent_streams, errors = await self._torrent_streams_service.find_by_imdb(
            user=user,
            imdb_id=imdb_id,
            series=series,
        )

        if user.only_best_torrent:
            torrent_streams = [torrent_streams[0]] if torrent_streams else []

        return torrent_streams, errors
