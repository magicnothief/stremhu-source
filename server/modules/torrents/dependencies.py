from common.database import get_db
from fastapi import Depends
from modules.indexer_accounts.dependencies import create_indexer_accounts_service
from modules.relay.dependencies import get_relay_service
from modules.torrent_files.dependencies import create_torrent_files_service
from modules.torrents.repository import TorrentRepository
from modules.torrents.service import TorrentsService
from sqlalchemy.orm import Session


def create_torrents_service(
    db: Session,
) -> TorrentsService:
    torrent_repository = TorrentRepository(db)
    relay_service = get_relay_service()
    torrent_files_service = create_torrent_files_service(db)
    indexer_accounts_service = create_indexer_accounts_service(db)

    return TorrentsService(
        torrent_repository=torrent_repository,
        relay_service=relay_service,
        torrent_files_service=torrent_files_service,
        indexer_accounts_service=indexer_accounts_service,
    )


def get_torrents_service(
    db: Session = Depends(get_db),
) -> TorrentsService:
    return create_torrents_service(db)
