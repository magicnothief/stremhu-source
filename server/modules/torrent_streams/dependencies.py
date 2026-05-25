from common.database import get_db
from fastapi import Depends
from modules.indexers.dependencies import (
    get_indexers_service,
)
from modules.indexers.service import IndexersService
from modules.persisted_torrents.dependencies import get_torrents_service
from modules.persisted_torrents.service import TorrentsService
from modules.torrent_files.dependencies import get_torrent_files_service
from modules.torrent_files.service import TorrentFilesService
from modules.torrent_streams.service import TorrentStreamsService
from sqlalchemy.orm import Session


def get_torrent_streams_service(
    db: Session = Depends(get_db),
    indexers_service: IndexersService = Depends(get_indexers_service),
    torrent_files_service: TorrentFilesService = Depends(get_torrent_files_service),
    torrents_service: TorrentsService = Depends(get_torrents_service),
) -> TorrentStreamsService:
    return TorrentStreamsService(
        db=db,
        indexers_service=indexers_service,
        torrent_files_service=torrent_files_service,
        torrents_service=torrents_service,
    )
