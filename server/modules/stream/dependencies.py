from common.database import get_db
from fastapi import Depends
from modules.indexers.dependencies import create_indexers_service
from modules.relay.dependencies import get_relay_service
from modules.stream.service import StreamService
from modules.torrent_files.dependencies import create_torrent_files_service
from modules.torrents.dependencies import create_torrents_service
from sqlalchemy.orm import Session


def create_stream_service(db: Session) -> StreamService:
    """Hozzárendeli a szervizt egy háttérfeladat vagy HTTP kérés adatbázis munkamenetéhez."""
    torrents_service = create_torrents_service(db)
    indexers_service = create_indexers_service(db)
    torrent_files_service = create_torrent_files_service(db)
    relay_service = get_relay_service()

    return StreamService(
        torrents_service=torrents_service,
        indexers_service=indexers_service,
        torrent_files_service=torrent_files_service,
        relay_service=relay_service,
    )


def get_stream_service(
    db: Session = Depends(get_db),
) -> StreamService:
    """FastAPI függőség-injektáló provider a StreamService példányosításához."""
    return create_stream_service(db)
