from common.enums import UserRole
from fastapi import APIRouter, Depends
from modules.auth.dependencies import SessionGuard
from modules.torrent_files.dependencies import get_torrent_files_service
from modules.torrent_files.service import TorrentFilesService
from modules.users.models import UserModel

router = APIRouter(
    prefix="/torrents/cache",
    tags=["Torrents Cache"],
)


@router.post(
    "/cleanup",
    operation_id="cleanup_torrents_cache",
)
def cleanup(
    torrent_files_service: TorrentFilesService = Depends(get_torrent_files_service),
    current_user: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
):
    """Elindítja az elavult és inaktív torrent cache fájlok manuális törlését (Retention Cleanup)."""
    torrent_files_service.run_retention_cleanup(retention_seconds=0)
