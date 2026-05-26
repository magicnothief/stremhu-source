import logging

from modules.preferences.models import PreferenceModel
from modules.preferences.seeds import DEFAULT_PREFERENCES
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class PreferencesService:
    def __init__(self, db: Session):
        self.db = db

    def sync_to_db(self):
        """Synchronizes the list of preference categories in the codebase with the database.

        Updates existing ones, inserts new ones, and deletes those that were removed
        from the code (along with all linked records via ON DELETE CASCADE).
        """
        logger.info(
            "🔄 Szinkronizálás: Preferencia kategóriák szinkronizálása az adatbázissal..."
        )

        code_ids = {pref.id for pref in DEFAULT_PREFERENCES}

        # 1. Töröljük a DB-ből azokat a kategóriákat, amelyek kikerültek a kódból
        # A cascade idegen kulcsok miatt ez automatikusan törli a hozzájuk tartozó attribútumokat/beállításokat is!
        deleted_count = (
            self.db.query(PreferenceModel)
            .filter(PreferenceModel.id.not_in(code_ids))
            .delete(synchronize_session=False)
        )
        if deleted_count > 0:
            logger.info(f"🗑️ Törölve {deleted_count} elavult kategória a DB-ből.")

        # 2. Beszúrás és frissítés (Upsert)
        for pref in DEFAULT_PREFERENCES:
            db_pref = (
                self.db.query(PreferenceModel)
                .filter(PreferenceModel.id == pref.id)
                .first()
            )

            if db_pref:
                if db_pref.name != pref.name or db_pref.description != pref.description:
                    db_pref.name = pref.name
                    db_pref.description = pref.description
            else:
                new_pref = PreferenceModel(
                    id=pref.id,
                    name=pref.name,
                    description=pref.description,
                )
                self.db.add(new_pref)

        self.db.commit()
