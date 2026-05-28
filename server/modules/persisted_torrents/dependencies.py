from common.database import get_db
from fastapi import Depends
from modules.indexers.dependencies import create_indexers_service
from modules.persisted_torrents.repository import TorrentRepository
from modules.persisted_torrents.service import TorrentsService
from modules.relay.dependencies import get_relay_service
from modules.torrent_files.dependencies import create_torrent_files_service
from sqlalchemy.orm import Session


def get_torrent_repository(
    db: Session = Depends(get_db),
) -> TorrentRepository:
    return TorrentRepository(db)


def create_torrents_service(db: Session) -> TorrentsService:
    relay_service = get_relay_service()
    torrent_repository = TorrentRepository(db)
    torrent_files_service = create_torrent_files_service(db)
    indexers_service = create_indexers_service(db)

    return TorrentsService(
        torrent_repository=torrent_repository,
        torrent_files_service=torrent_files_service,
        indexers_service=indexers_service,
        relay_service=relay_service,
    )


def get_torrents_service(
    db: Session = Depends(get_db),
) -> TorrentsService:
    return create_torrents_service(db)
