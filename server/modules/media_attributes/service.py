import pydash
from common.logger import logger
from modules.media_attributes.models import MediaAttributeModel
from modules.media_attributes.repository import MediaAttributesRepository
from modules.media_attributes.seeds import DEFAULT_ATTRIBUTES


class MediaAttributesService:
    def __init__(self, repository: MediaAttributesRepository):
        self._repository = repository

    def sync_to_db(self) -> None:
        """
        Synchronizes the predefined media attributes defined in code (seeds.py) with the database.
        It updates existing records, adds new ones, and deletes those that no longer exist in code.
        """
        code_ids = {attr.id for attr in DEFAULT_ATTRIBUTES}

        deleted_count = self._repository.delete_excluding_ids(code_ids)
        if deleted_count > 0:
            logger.info(f"🗑️ Törölve {deleted_count} elavult media attribútum a DB-ből.")

        # Kérjük le a meglévő rekordokat
        db_attributes_map: dict[str, MediaAttributeModel] = {}
        db_records = self._repository.db.query(MediaAttributeModel).all()
        for db_record in db_records:
            db_attributes_map[db_record.id] = db_record

        # Hozzáadjuk a hiányzókat és frissítjük a megváltozottakat
        fields = ["name", "preference_id", "pattern", "short_name", "order"]
        for index, code_attribute in enumerate(DEFAULT_ATTRIBUTES):
            code_attribute.order = index

            if code_attribute.id in db_attributes_map:
                db_attribute = db_attributes_map[code_attribute.id]

                if pydash.pick(db_attribute, *fields) != pydash.pick(
                    code_attribute, *fields
                ):
                    for field in fields:
                        setattr(db_attribute, field, getattr(code_attribute, field))
            else:
                new_attribute = MediaAttributeModel(
                    id=code_attribute.id,
                    name=code_attribute.name,
                    preference_id=code_attribute.preference_id,
                    pattern=code_attribute.pattern,
                    short_name=code_attribute.short_name,
                    order=code_attribute.order,
                )
                self._repository.add(new_attribute)
