import logging
from typing import Callable

from fastapi import HTTPException, status
from modules.indexers.definitions.base_indexer_definition import BaseIndexerDefinition
from modules.indexers.definitions.exceptions import (
    AuthenticationException,
    CredentialsRequiredException,
)
from modules.indexers.definitions.integrations import discover_indexer_definitions
from modules.indexers.definitions.schemas import IndexerDefinitionLoginRequest
from modules.indexers.schemas import LoginIndexer

logger = logging.getLogger(__name__)


class IndexerDefinitionsService:
    """
    A NestJS TrackerIndexersService portolása.

    Az integrations/ mappából automatikusan felderíti az adapter osztályokat,
    példányosítja őket, és nyilvántartja egy szótárban.
    """

    def __init__(self, credentials_provider: Callable) -> None:
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

    # --- TODO: login() – TrackerAccountsService integrációval együtt kell megvalósítani ---
    # A NestJS TrackerIndexersService.login() ellenőrzi, hogy a fiók már be van-e jelentkezve
    # (trackerAccountsService.findOne()), majd az adapter.login()-t hívja, végül
    # trackerAccountsService.create()-vel elmenti. Ez a logika a TrackerAccountsService
    # portolása után egészítendő ki.

    async def login(self, payload: LoginIndexer) -> None:
        """
        Bejelentkezés egy adott tracker adapterbe.

        A NestJS TrackerIndexersService.login() portolása.

        TODO: TrackerAccountsService integrációja (duplikált bejelentkezés ellenőrzése
              és fiók mentése) a service portolása után.
        """
        indexer_definition = self.find_one_by_id(payload.indexer_id)
        credential = IndexerDefinitionLoginRequest(
            username=payload.username, password=payload.password
        )

        try:
            await indexer_definition.login(credential)
        except CredentialsRequiredException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except AuthenticationException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bejelentkezés közben hiba történt, próbáld újra!",
            )

    def find_all(self) -> list[BaseIndexerDefinition]:
        """Az összes regisztrált adapter visszaadása – a NestJS find() megfelelője."""
        return list(self._definitions.values())

    def find_one_by_id(self, tracker_id: str) -> BaseIndexerDefinition:
        """
        Egy adapter keresése ID alapján.

        A NestJS findOneById() megfelelője – 400-as kivételt dob, ha nincs regisztrálva.
        """
        adapter = self._definitions.get(tracker_id)

        if not adapter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nem regisztrált tracker adapter: {tracker_id}",
            )

        return adapter

    async def close_all(self) -> None:
        """Lezárja az összes adapter HTTP kliensét (alkalmazás leállásakor)."""
        for adapter in self._definitions.values():
            await adapter.close()
