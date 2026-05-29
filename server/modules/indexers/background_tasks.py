import logging

from common.database import db_session
from modules.indexers.dependencies import create_indexers_service

logger = logging.getLogger(__name__)


async def run_indexers_cleanup() -> None:
    """A bejelentkezett indexerek napi karbantartási feladatainak futtatása."""
    logger.info("🔄 Kezdődik a támogatott indexerek karbantartási takarítása...")
    try:
        with db_session() as db:
            indexers_service = create_indexers_service(db)
            await indexers_service.run_maintenance_cleanup()
        logger.info("✅ Az indexerek karbantartási takarítása befejeződött.")
    except Exception as e:
        logger.error(
            f"🚨 Hiba történt az indexerek karbantartási takarítása során: {e}",
            exc_info=e,
        )
