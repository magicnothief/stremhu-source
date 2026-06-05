from common.database import get_db
from fastapi import Depends
from modules.kodi.service import KodiService
from modules.torrent_streams.dependencies import (
    create_torrent_name_parser_service,
    create_torrent_streams_service,
)
from modules.torrent_streams.name_parser_service import TorrentNameParserService
from sqlalchemy.orm import Session


def create_kodi_service(
    db: Session,
    torrent_name_parser_service: TorrentNameParserService,
) -> KodiService:
    """Hozzárendeli a szervizt egy háttérfeladat vagy HTTP kérés adatbázis munkamenetéhez."""
    torrent_streams_service = create_torrent_streams_service(
        db, torrent_name_parser_service
    )
    return KodiService(torrent_streams_service=torrent_streams_service)


def get_kodi_service(
    db: Session = Depends(get_db),
    torrent_name_parser_service: TorrentNameParserService = Depends(
        create_torrent_name_parser_service
    ),
) -> KodiService:
    """FastAPI függőség-injektáló provider a KodiService példányosításához."""
    return create_kodi_service(db, torrent_name_parser_service)
