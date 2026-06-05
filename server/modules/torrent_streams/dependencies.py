from common.database import get_db
from fastapi import Depends, Request
from modules.settings.dependencies import create_settings_service
from modules.torrent_source_provider.dependencies import (
    create_torrent_source_provider_service,
)
from modules.torrent_streams.name_parser_service import TorrentNameParserService
from modules.torrent_streams.service import TorrentStreamsService
from modules.torrents.dependencies import create_torrents_service
from sqlalchemy.orm import Session


def create_torrent_name_parser_service(request: Request) -> TorrentNameParserService:
    return request.app.state.torrent_name_parser


def create_torrent_streams_service(
    db: Session,
    torrent_name_parser_service: TorrentNameParserService,
) -> TorrentStreamsService:
    torrent_source_provider_service = create_torrent_source_provider_service(db)
    torrents_service = create_torrents_service(db)
    settings_service = create_settings_service(db)

    return TorrentStreamsService(
        db=db,
        torrent_source_provider_service=torrent_source_provider_service,
        torrents_service=torrents_service,
        torrent_name_parser_service=torrent_name_parser_service,
        settings_service=settings_service,
    )


def get_torrent_streams_service(
    db: Session = Depends(get_db),
    torrent_name_parser_service: TorrentNameParserService = Depends(
        create_torrent_name_parser_service
    ),
) -> TorrentStreamsService:
    return create_torrent_streams_service(db, torrent_name_parser_service)
