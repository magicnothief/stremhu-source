import pydash
from common.logger import logger
from fastapi import HTTPException, status
from modules.indexer_definitions.base_indexer_definition import BaseIndexerDefinition
from modules.indexer_definitions.integrations import discover_indexer_definitions
from modules.indexer_definitions.models import IndexerDefinitionModel
from modules.indexer_definitions.protocols import IndexerAccountStorage
from modules.preferences.constants import PreferenceKey
from sqlalchemy.orm import Session


class IndexerDefinitionsService:
    """
    Az integrations/ mappából automatikusan felderíti az adapter osztályokat,
    példányosítja őket, és nyilvántartja egy szótárban.
    """

    def __init__(
        self,
        indexer_account_storage: IndexerAccountStorage | None = None,
    ):
        self._definitions: dict[str, BaseIndexerDefinition] = {}

        for definition_class in discover_indexer_definitions():
            instance = definition_class(indexer_account_storage)
            self._definitions[instance.id] = instance
            logger.debug("Definition registered: %s (%s)", instance.name, instance.id)

    def get_list(self) -> list[BaseIndexerDefinition]:
        """Az összes regisztrált adapter visszaadása."""
        return list(self._definitions.values())

    def get_by_id(self, indexer_id: str) -> BaseIndexerDefinition:
        """
        Egy adapter keresése ID alapján.
        """
        adapter = self._definitions.get(indexer_id)

        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nem regisztrált tracker adapter: {indexer_id}",
            )

        return adapter

    async def close_all(self) -> None:
        """Lezárja az összes adapter HTTP kliensét (alkalmazás leállásakor)."""
        for adapter in self._definitions.values():
            await adapter.close()

    def sync_to_db(self, db: Session):
        """Szinkronizálja az integrations/ mappából dinamikusan felderített indexereket az adatbázissal."""

        discovered_definitions = self.get_list()

        def get_sort_key(instance: BaseIndexerDefinition) -> tuple[int, str]:
            idx = instance.id.lower()
            if idx == "ncore":
                return (0, "")
            if idx == "bithumen":
                return (1, "")
            return (2, instance.name.lower())

        discovered_definitions.sort(key=get_sort_key)

        discovered_ids = {instance.id for instance in discovered_definitions}

        deleted_count = (
            db.query(IndexerDefinitionModel)
            .filter(IndexerDefinitionModel.id.not_in(discovered_ids))
            .delete(synchronize_session=False)
        )
        if deleted_count > 0:
            logger.info(
                f"🗑️ Törölve {deleted_count} elavult indexer definíció a DB-ből."
            )

        # Meglévő rekordok lekérése egyetlen lekérdezéssel
        db_definitions_map = {
            db_def.id: db_def for db_def in db.query(IndexerDefinitionModel).all()
        }

        fields = ["name", "url", "details_path", "requires_full_download", "order"]
        for index, instance in enumerate(discovered_definitions):
            instance_data = {
                "name": instance.name,
                "url": instance.url,
                "details_path": instance.details_path,
                "requires_full_download": instance.requires_full_download,
                "order": index,
            }

            if instance.id in db_definitions_map:
                db_definition = db_definitions_map[instance.id]

                if pydash.pick(db_definition, *fields) != instance_data:
                    for field in fields:
                        setattr(db_definition, field, instance_data[field])
            else:
                new_definition = IndexerDefinitionModel(
                    id=instance.id,
                    preference_id=PreferenceKey.SITE,
                    **instance_data,
                )
                db.add(new_definition)
