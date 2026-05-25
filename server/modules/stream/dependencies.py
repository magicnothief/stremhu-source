from functools import lru_cache

from fastapi import Depends
from modules.libtorrent_client.dependencies import get_libtorrent_client_service
from modules.libtorrent_client.service import LibtorrentClientService
from modules.stream.service import StreamService


@lru_cache
def get_stream_service(
    libtorrent_client_service: LibtorrentClientService = Depends(
        get_libtorrent_client_service
    ),
) -> StreamService:
    return StreamService(
        libtorrent_client_service=libtorrent_client_service,
    )
