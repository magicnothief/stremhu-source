from common.database import get_db
from fastapi import Depends
from modules.libtorrent_client.dependencies import get_libtorrent_client_service
from modules.libtorrent_client.service import LibtorrentClientService
from modules.torrent_files.repository import TorrentFilesRepository
from modules.torrent_files.service import TorrentFilesService
from sqlalchemy.orm import Session


def _get_torrent_files_repository(
    db: Session = Depends(get_db),
) -> TorrentFilesRepository:
    return TorrentFilesRepository(db)


def get_torrent_files_service(
    repository: TorrentFilesRepository = Depends(_get_torrent_files_repository),
    libtorrent_client_service: LibtorrentClientService = Depends(
        get_libtorrent_client_service
    ),
) -> TorrentFilesService:
    """FastAPI függőség-injektáló a tiszta TorrentFilesService példányosításához."""
    return TorrentFilesService(repository, libtorrent_client_service)
