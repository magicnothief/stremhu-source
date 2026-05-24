from functools import lru_cache

from fastapi import Depends
from modules.libtorrent_client.service import LibtorrentClientService
from modules.persisted_torrents.service import TorrentsService
from modules.stream.dependencies import (
    get_libtorrent_client_service,
    get_stream_service,
)
from modules.stream.service import StreamService


@lru_cache
def get_torrents_service(
    libtorrent_client_service: LibtorrentClientService = Depends(
        get_libtorrent_client_service
    ),
    stream_service: StreamService = Depends(get_stream_service),
) -> TorrentsService:
    return TorrentsService(
        libtorrent_client_service=libtorrent_client_service,
        stream_service=stream_service,
    )
