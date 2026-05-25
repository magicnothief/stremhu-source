import logging

from fastapi import HTTPException, status
from modules.indexers.definitions.base_indexer_definition import BaseIndexerDefinition
from modules.indexers.definitions.integrations import discover_indexer_definitions
from modules.indexers.definitions.schemas import CredentialsProvider

logger = logging.getLogger(__name__)


class IndexerDefinitionsService:
    """
    Az integrations/ mappából automatikusan felderíti az adapter osztályokat,
    példányosítja őket, és nyilvántartja egy szótárban.
    """

    def __init__(self, credentials_provider: CredentialsProvider = None) -> None:
        self._definitions: dict[str, BaseIndexerDefinition] = {}

        for definition_class in discover_indexer_definitions():
            instance = definition_class(credentials_provider)
            self._definitions[instance.id] = instance
            logger.debug("Definition registered: %s (%s)", instance.name, instance.id)

        logger.info(
            "%d tracker adapter betöltve: %s",
            len(self._definitions),
            ", ".join(self._definitions.keys()),
        )

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
