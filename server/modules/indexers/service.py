import asyncio
import logging

from fastapi import HTTPException, status
from modules.indexers.definitions.exceptions import (
    AuthenticationException,
    CredentialsRequiredException,
)
from modules.indexers.definitions.service import IndexerDefinitionsService
from modules.indexers.models import IndexerModel
from modules.indexers.repository import IndexersRepository
from modules.indexers.schemas import IndexerLogin

logger = logging.getLogger(__name__)


class IndexersService:
    def __init__(
        self,
        indexers_repository: IndexersRepository,
        indexer_definitions_service: IndexerDefinitionsService,
    ):
        self._indexers_repository = indexers_repository
        self._indexer_definitions_service = indexer_definitions_service

    async def login(self, payload: IndexerLogin) -> None:
        indexer = await asyncio.to_thread(self.get_by_id, payload.indexer_id)

        if indexer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A megadott indexer már be van jelentkezve!",
            )

        try:
            await self._indexer_definitions_service.login(payload)
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

    def get_by_id(self, id: str) -> IndexerModel | None:
        return self._indexers_repository.find_by_id(id)

    def get_by_id_or_raise(self, id: str) -> IndexerModel:
        indexer = self.get_by_id(id)
        if indexer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nem található indexer!",
            )
        return indexer

    def get_list(self) -> list[IndexerModel]:
        return list(self._indexers_repository.find_all())
