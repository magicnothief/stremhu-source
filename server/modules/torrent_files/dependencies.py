from common.database import get_db
from fastapi import Depends
from modules.relay.dependencies import get_relay_service
from modules.torrent_files.repository import TorrentFilesRepository
from modules.torrent_files.service import TorrentFilesService
from sqlalchemy.orm import Session


def create_torrent_files_service(db: Session) -> TorrentFilesService:
    repository = TorrentFilesRepository(db)
    relay_service = get_relay_service()
    return TorrentFilesService(repository, relay_service)


def get_torrent_files_service(
    db: Session = Depends(get_db),
) -> TorrentFilesService:
    return create_torrent_files_service(db)
