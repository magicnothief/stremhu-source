from fastapi import Depends
from modules.indexers.dependencies import get_indexers_service
from modules.indexers.service import IndexersService
from modules.persisted_torrents.dependencies import get_torrents_service
from modules.persisted_torrents.service import TorrentsService
from modules.relay.dependencies import get_relay_service
from modules.relay.service import RelayService
from modules.stream.service import StreamService
from modules.torrent_files.dependencies import get_torrent_files_service
from modules.torrent_files.service import TorrentFilesService


def get_stream_service(
    torrents_service: TorrentsService = Depends(get_torrents_service),
    indexers_service: IndexersService = Depends(get_indexers_service),
    torrent_files_service: TorrentFilesService = Depends(get_torrent_files_service),
    relay_service: RelayService = Depends(get_relay_service),
) -> StreamService:
    return StreamService(
        torrents_service=torrents_service,
        indexers_service=indexers_service,
        torrent_files_service=torrent_files_service,
        relay_service=relay_service,
    )
