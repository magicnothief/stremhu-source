import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from modules.stremio.dependencies import (
    get_current_user_by_token,
    get_parsed_catalog_id,
    get_parsed_extra,
    get_parsed_stream_id,
    get_stremio_service,
)
from modules.stremio.enums import MediaType
from modules.stremio.schemas import (
    Manifest,
    MetaResponse,
    ParsedCatalogId,
    ParsedExtra,
    ParsedStreamId,
    StremioCatalogResponse,
    StremioStreamsResponse,
)
from modules.stremio.service import StremioService
from modules.users.models import UserModel

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/{token}/stremio",
    tags=["Stremio"],
)


# ──────────────────────────────────────────────
# Manifest & Configure
# ──────────────────────────────────────────────


@router.get(
    "/manifest.json",
    response_model=Manifest,
    operation_id="stremio_manifest",
)
def manifest(
    stremio_service: StremioService = Depends(get_stremio_service),
    current_user: UserModel = Depends(get_current_user_by_token),
) -> Manifest:
    return stremio_service.manifest()


@router.get(
    "/configure",
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
    operation_id="stremio_configure",
)
def configure(
    current_user: UserModel = Depends(get_current_user_by_token),
) -> RedirectResponse:
    return RedirectResponse(url="/", status_code=status.HTTP_308_PERMANENT_REDIRECT)


# ──────────────────────────────────────────────
# Streams
# ──────────────────────────────────────────────


@router.get(
    "/stream/{media_type}/{stream_id}.json",
    response_model=StremioStreamsResponse,
    operation_id="stremio_streams",
)
async def streams(
    media_type: MediaType,
    parsed_id: ParsedStreamId = Depends(get_parsed_stream_id),
    stremio_service: StremioService = Depends(get_stremio_service),
    current_user: UserModel = Depends(get_current_user_by_token),
) -> StremioStreamsResponse:
    stream_list = await stremio_service.get_streams(current_user, parsed_id)
    return StremioStreamsResponse(streams=stream_list)


# ──────────────────────────────────────────────
# Catalogs
# ──────────────────────────────────────────────


@router.get(
    "/catalog/{media_type}/{catalog_id}.json",
    response_model=StremioCatalogResponse,
    operation_id="stremio_catalog",
)
async def catalog(
    media_type: MediaType,
    catalog_id: str,
    stremio_service: StremioService = Depends(get_stremio_service),
    current_user: UserModel = Depends(get_current_user_by_token),
) -> StremioCatalogResponse:
    return await _get_catalog(stremio_service, media_type, catalog_id)


@router.get(
    "/catalog/{media_type}/{catalog_id}/{extra}.json",
    response_model=StremioCatalogResponse,
    operation_id="stremio_catalog_with_extra",
)
async def catalog_with_extra(
    media_type: MediaType,
    catalog_id: str,
    parsed_extra: ParsedExtra = Depends(get_parsed_extra),
    stremio_service: StremioService = Depends(get_stremio_service),
    current_user: UserModel = Depends(get_current_user_by_token),
) -> StremioCatalogResponse:
    return await _get_catalog(stremio_service, media_type, catalog_id, parsed_extra)


async def _get_catalog(
    stremio_service: StremioService,
    media_type: MediaType,
    catalog_id: str,
    extra: ParsedExtra | None = None,
) -> StremioCatalogResponse:
    """Közös katalógus logika – a NestJS getCatalog() privát metódus portolása."""
    from modules.stremio.constants import SEARCH_ID
    from modules.stremio.schemas import ParsedExtra

    if extra is None:
        extra = ParsedExtra()

    search = extra.search

    if media_type != MediaType.MOVIE or catalog_id != SEARCH_ID or not search:
        return StremioCatalogResponse(metas=[])

    parts = search.split("-", 1)
    if len(parts) < 2 or parts[0] != "t":
        return StremioCatalogResponse(metas=[])

    torrent_id = parts[1]

    try:
        meta_previews = await stremio_service.get_metas(torrent_id)
    except Exception as e:
        logger.error("A lista lekérésénél hiba történt: %s", e)
        meta_previews = []

    return StremioCatalogResponse(metas=meta_previews)


# ──────────────────────────────────────────────
# Meta
# ──────────────────────────────────────────────


@router.get(
    "/meta/{media_type}/{meta_id}.json",
    response_model=MetaResponse,
    operation_id="stremio_meta",
)
async def meta(
    media_type: MediaType,
    parsed_id: ParsedCatalogId = Depends(get_parsed_catalog_id),
    stremio_service: StremioService = Depends(get_stremio_service),
    current_user: UserModel = Depends(get_current_user_by_token),
) -> MetaResponse:
    if media_type != MediaType.MOVIE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    result = await stremio_service.get_meta(parsed_id.tracker_id, parsed_id.torrent_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return MetaResponse(meta=result)
