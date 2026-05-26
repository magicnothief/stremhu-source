import logging

from modules.roles.models import RoleModel
from modules.roles.seeds import DEFAULT_ROLES
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class RolesService:
    def __init__(self, db: Session):
        self.db = db

    def sync_to_db(self) -> None:
        """Synchronizes the list of roles in the codebase with the database.

        Updates existing ones, inserts new ones, and deletes those that were
        removed from the code (along with their database relations via ON DELETE CASCADE).
        """
        logger.info("🔄 Szinkronizálás: Szerepkörök szinkronizálása az adatbázissal...")

        code_ids = {role.id for role in DEFAULT_ROLES}

        # 1. Töröljük azokat a szerepköröket a DB-ből, amelyek kikerültek a kódból
        deleted_count = (
            self.db.query(RoleModel)
            .filter(RoleModel.id.not_in(code_ids))
            .delete(synchronize_session=False)
        )
        if deleted_count > 0:
            logger.info(f"🗑️ Törölve {deleted_count} elavult szerepkör a DB-ből.")

        # 2. Upsert: frissítés ha változott a név, egyébként beszúrás
        for code_role in DEFAULT_ROLES:
            db_role = (
                self.db.query(RoleModel).filter(RoleModel.id == code_role.id).first()
            )

            if db_role:
                if db_role.name != code_role.name:
                    db_role.name = code_role.name
            else:
                self.db.add(RoleModel(id=code_role.id, name=code_role.name))

        self.db.commit()
