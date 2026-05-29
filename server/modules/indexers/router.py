from fastapi import APIRouter, Depends, status
from modules.auth.dependencies import SessionGuard
from modules.indexers.dependencies import get_indexers_service
from modules.indexers.schemas import Indexer, IndexerLogin, IndexerUpdate
from modules.indexers.service import IndexersService
from modules.roles.enums import UserRole
from modules.users.models import UserModel

router = APIRouter(
    prefix="/indexers",
    tags=["Indexers"],
)


@router.get(
    "/",
    response_model=list[Indexer],
)
async def get_list(
    indexers_service: IndexersService = Depends(get_indexers_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
):
    """Bejelentkezett indexerek listájának lekérése."""
    return indexers_service.get_list()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Indexer,
)
async def login(
    payload: IndexerLogin,
    indexers_service: IndexersService = Depends(get_indexers_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
):
    """Bejelentkezés egy új indexerre."""
    return await indexers_service.login(payload)


@router.post(
    "/cleanup",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cleanup(
    indexers_service: IndexersService = Depends(get_indexers_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
):
    """Karbantartási takarítás manuális futtatása."""
    await indexers_service.run_maintenance_cleanup()


@router.put(
    "/{id}",
    response_model=Indexer,
)
async def update(
    id: str,
    payload: IndexerUpdate,
    indexers_service: IndexersService = Depends(get_indexers_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
):
    """Egy indexer beállításainak módosítása."""
    return await indexers_service.update(id, payload)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    id: str,
    indexers_service: IndexersService = Depends(get_indexers_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
):
    """Indexer törlése/kijelentkeztetése."""
    await indexers_service.delete(id)
