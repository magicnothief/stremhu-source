from common.database import get_db
from fastapi import Depends, Path
from modules.settings.dependencies import create_settings_service
from modules.stremio.schemas import ParsedCatalogId, ParsedExtra, ParsedStreamId
from modules.stremio.service import StremioService
from modules.stremio.utils import parse_catalog_id, parse_extra, parse_stream_id
from modules.torrent_streams.dependencies import (
    create_torrent_name_parser_service,
    create_torrent_streams_service,
)
from modules.torrent_streams.name_parser_service import TorrentNameParserService
from sqlalchemy.orm import Session


def create_stremio_service(
    db: Session,
    torrent_name_parser_service: TorrentNameParserService,
) -> StremioService:
    torrent_streams_service = create_torrent_streams_service(
        db, torrent_name_parser_service
    )
    settings_service = create_settings_service(db)

    return StremioService(
        torrent_streams_service=torrent_streams_service,
        settings_service=settings_service,
    )


def get_stremio_service(
    db: Session = Depends(get_db),
    torrent_name_parser_service: TorrentNameParserService = Depends(
        create_torrent_name_parser_service
    ),
) -> StremioService:
    return create_stremio_service(db, torrent_name_parser_service)


def get_parsed_stream_id(
    stream_id: str = Path(
        ..., description="Stream azonosító (IMDB ID vagy torrent ID)"
    ),
) -> ParsedStreamId:
    return parse_stream_id(stream_id)


def get_parsed_catalog_id(
    meta_id: str = Path(
        ..., description="Katalógus / Meta azonosító (trackerId:torrentId)"
    ),
) -> ParsedCatalogId | None:
    return parse_catalog_id(meta_id)


def get_parsed_extra(
    extra: str = Path(
        ..., description="Kiegészítő szűrési paraméterek (pl. search=film&skip=20)"
    ),
) -> ParsedExtra:
    return parse_extra(extra)
