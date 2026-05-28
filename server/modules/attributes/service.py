import logging

from modules.attributes.models import AttributeModel
from modules.attributes.repository import AttributesRepository
from modules.attributes.seeds import DEFAULT_ATTRIBUTES
from modules.preferences.enums import PreferenceEnum

logger = logging.getLogger(__name__)


class AttributesService:
    def __init__(self, repository: AttributesRepository):
        """Initializes the service with the attributes repository."""
        self._repository = repository

    def get_all(self) -> list[AttributeModel]:
        """Fetches all attributes."""
        return self._repository.find_all()

    def get_by_preference(self, preference: PreferenceEnum) -> list[AttributeModel]:
        """Fetches all attributes belonging to a specific preference category."""
        return self._repository.find_by_preference(preference)

    def get_all_as_map(self) -> dict[str, AttributeModel]:
        """Fetches all attributes as a dictionary mapping ID to AttributeModel."""
        return {model.id: model for model in self.get_all()}

    def sync_to_db(self) -> None:
        """Synchronizes the list of attributes in the codebase with the database.

        Updates existing ones, inserts new ones, and deletes those that were removed
        from the code (along with their database relations via ON DELETE CASCADE).
        """
        logger.info(
            "🔄 Szinkronizálás: Attribútumok szinkronizálása az adatbázissal..."
        )

        code_ids = {attr.id for attr in DEFAULT_ATTRIBUTES}

        # 1. Töröljük azokat az attribútumokat a DB-ből, amelyek kikerültek a kódból
        deleted_count = self._repository.delete_excluding_ids(code_ids)
        if deleted_count > 0:
            logger.info(f"🗑️ Törölve {deleted_count} elavult attribútum a DB-ből.")

        # 2. Beszúrás és frissítés (Upsert)
        for code_attribute in DEFAULT_ATTRIBUTES:
            db_attribute = self._repository.find_by_id(code_attribute.id)

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
                self._repository.add(new_attribute)

        self._repository.commit()
