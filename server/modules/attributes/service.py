import logging
from typing import Dict

from modules.attributes.models import AttributeModel
from modules.attributes.seeds import DEFAULT_ATTRIBUTES
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AttributesService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[AttributeModel]:
        return self.db.query(AttributeModel).all()

    def get_all_as_map(self) -> Dict[str, AttributeModel]:
        return {model.id: model for model in self.get_all()}

    def sync_to_db(self):
        """Synchronizes the list of attributes in the codebase with the database.

        Updates existing ones, inserts new ones, and deletes those that were removed
        from the code (along with their database relations via ON DELETE CASCADE).
        """
        logger.info(
            "🔄 Szinkronizálás: Attribútumok szinkronizálása az adatbázissal..."
        )

        code_ids = {attr.id for attr in DEFAULT_ATTRIBUTES}

        # 1. Töröljük azokat az attribútumokat a DB-ből, amelyek kikerültek a kódból
        # A Foreign Key szinten beállított CASCADE törlés miatt ez mindenhonnan törli a kapcsolatokat is!
        deleted_count = (
            self.db.query(AttributeModel)
            .filter(AttributeModel.id.not_in(code_ids))
            .delete(synchronize_session=False)
        )
        if deleted_count > 0:
            logger.info(f"🗑️ Törölve {deleted_count} elavult attribútum a DB-ből.")

        # 2. Beszúrás és frissítés (Upsert)
        for code_attribute in DEFAULT_ATTRIBUTES:
            db_attribute = (
                self.db.query(AttributeModel)
                .filter(AttributeModel.id == code_attribute.id)
                .first()
            )

            if db_attribute:
                if (
                    db_attribute.name != code_attribute.name
                    or db_attribute.preference_id != code_attribute.preference_id
                ):
                    db_attribute.name = code_attribute.name
                    db_attribute.preference_id = code_attribute.preference_id
            else:
                new_attribute = AttributeModel(
                    id=code_attribute.id,
                    name=code_attribute.name,
                    preference_id=code_attribute.preference_id,
                )
                self.db.add(new_attribute)

        self.db.commit()
