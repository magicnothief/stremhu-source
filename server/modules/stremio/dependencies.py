import uuid

from common.database import get_db
from fastapi import Depends, HTTPException, Path, status
from modules.stremio.schemas import ParsedCatalogId, ParsedExtra, ParsedStreamId
from modules.stremio.service import StremioService
from modules.stremio.utils import parse_catalog_id, parse_extra, parse_stream_id
from modules.torrent_streams.dependencies import get_torrent_streams_service
from modules.torrent_streams.service import TorrentStreamsService
from modules.users.models import UserModel
from sqlalchemy.orm import Session


def get_stremio_service(
    torrent_streams_service: TorrentStreamsService = Depends(
        get_torrent_streams_service
    ),
) -> StremioService:
    """FastAPI függőség-injektáló provider a StremioService példányosításához."""
    return StremioService(torrent_streams_service=torrent_streams_service)


def get_current_user_by_token(
    token: str = Path(..., description="Felhasználói token (UUID v4)"),
    db: Session = Depends(get_db),
) -> UserModel:
    """
    Token alapú hitelesítés – a NestJS TokenGuard megfelelője.

    Az URL path paraméterből olvassa a tokent, validálja UUID-ként,
    és kikeresi a felhasználót az adatbázisból.
    """
    try:
        token_uuid = uuid.UUID(token, version=4)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A kulcs érvénytelen vagy nincs megadva!",
        )

    user = db.query(UserModel).filter(UserModel.token == token_uuid).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A kulcs érvénytelen!",
        )

    return user


def get_parsed_stream_id(
    stream_id: str = Path(
        ..., description="Stream azonosító (IMDB ID vagy torrent ID)"
    ),
) -> ParsedStreamId:
    """Automatikus parse-olás a Stremio stream azonosítóhoz (pl. tt1234567, stremhu-source:tracker:id)."""
    return parse_stream_id(stream_id)


def get_parsed_catalog_id(
    meta_id: str = Path(
        ..., description="Katalógus / Meta azonosító (trackerId:torrentId)"
    ),
) -> ParsedCatalogId:
    """Automatikus parse-olás a Stremio catalog / meta azonosítóhoz (pl. trackerId:torrentId)."""
    return parse_catalog_id(meta_id)


def get_parsed_extra(
    extra: str = Path(
        ..., description="Kiegészítő szűrési paraméterek (pl. search=film&skip=20)"
    ),
) -> ParsedExtra:
    """Automatikus parse-olás a Stremio extra (pl. search/skip) paraméterekhez."""
    return parse_extra(extra)
