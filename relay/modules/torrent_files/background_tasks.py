import logging

from common.database import db_session
from modules.libtorrent_client.dependencies import get_libtorrent_client_service
from modules.torrent_files.repository import TorrentFilesRepository
from modules.torrent_files.service import TorrentFilesService

logger = logging.getLogger(__name__)


def run_torrent_files_retention_cleanup():
    """Tisztító feladat az elavult és inaktív torrent gyorsítótár rekordokhoz (APScheduler-hez)."""
    logger.info(
        "⏰ Automatikus gyorsítótár (torrent_files) tisztítás indítása (APScheduler)..."
    )

    try:
        with db_session() as db:
            repository = TorrentFilesRepository(db)
            libtorrent_service = get_libtorrent_client_service()
            torrent_files_service = TorrentFilesService(repository, libtorrent_service)
            torrent_files_service.run_retention_cleanup()
        logger.info("✅ Automatikus gyorsítótár tisztítás sikeresen befejeződött.")
    except Exception as e:
        logger.error(
            f"❌ Hiba történt az automatikus gyorsítótár tisztítás közben: {e}"
        )
