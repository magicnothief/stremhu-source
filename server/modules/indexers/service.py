import asyncio
import logging

from fastapi import HTTPException, status
from modules.indexers.definitions.exceptions import (
    AuthenticationException,
    CredentialsRequiredException,
)
from modules.indexers.definitions.schemas import (
    IndexerDefinitionLogin,
)
from modules.indexers.definitions.service import IndexerDefinitionsService
from modules.indexers.models import IndexerModel
from modules.indexers.repository import IndexersRepository
from modules.indexers.schemas import DownloadedTorrentFile, IndexerLogin, IndexerTorrent

logger = logging.getLogger(__name__)


class IndexersService:
    def __init__(
        self,
        indexers_repository: IndexersRepository,
        indexer_definitions_service: IndexerDefinitionsService,
    ):
        self._indexers_repository = indexers_repository
        self._indexer_definitions_service = indexer_definitions_service

    async def login(self, payload: IndexerLogin) -> IndexerModel:
        indexer = await asyncio.to_thread(self.get_by_id, payload.indexer_id)

        if indexer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A megadott indexer már be van jelentkezve!",
            )

        indexer_definition = self._indexer_definitions_service.get_by_id(
            payload.indexer_id
        )

        try:
            await indexer_definition.login(
                IndexerDefinitionLogin(
                    username=payload.username,
                    password=payload.password,
                )
            )

            indexer = IndexerModel(
                id=payload.indexer_id,
                username=payload.username,
                password=payload.password,
            )
            return await asyncio.to_thread(self._indexers_repository.create, indexer)
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

    async def get_torrents_by_torrent_id(
        self, torrent_id: str
    ) -> tuple[list[IndexerTorrent], list[str]]:
        indexers = await asyncio.to_thread(self.get_list)

        async def fetch_and_map(indexer_id: str) -> IndexerTorrent:
            indexer_definition = self._indexer_definitions_service.get_by_id(indexer_id)
            indexer_definition_torrent = await indexer_definition.find_torrent_by_id(
                torrent_id
            )
            return IndexerTorrent(
                indexer_id=indexer_id,
                torrent_id=indexer_definition_torrent.torrent_id,
                download_url=indexer_definition_torrent.download_url,
                imdb_id=indexer_definition_torrent.imdb_id,
                seeders=indexer_definition_torrent.seeders,
                fallback_attributes=indexer_definition_torrent.fallback_attributes,
            )

        tasks = [fetch_and_map(indexer.id) for indexer in indexers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        indexer_torrents: list[IndexerTorrent] = []
        errors: list[str] = []

        for result in results:
            if isinstance(result, BaseException):
                errors.append(str(result))
            else:
                indexer_torrents.append(result)

        return indexer_torrents, errors

    async def get_torrent_by_torrent_id(
        self,
        indexer_id: str,
        torrent_id: str,
    ) -> IndexerTorrent:
        indexer = await asyncio.to_thread(self.get_by_id_or_raise, indexer_id)

        indexer_definition = self._indexer_definitions_service.get_by_id(indexer.id)
        indexer_definition_torrent = await indexer_definition.find_torrent_by_id(
            torrent_id
        )
        return IndexerTorrent(
            indexer_id=indexer.id,
            torrent_id=indexer_definition_torrent.torrent_id,
            download_url=indexer_definition_torrent.download_url,
            imdb_id=indexer_definition_torrent.imdb_id,
            seeders=indexer_definition_torrent.seeders,
            fallback_attributes=indexer_definition_torrent.fallback_attributes,
        )

    async def get_torrents_by_imdb_id(
        self, imdb_id: str
    ) -> tuple[list[IndexerTorrent], list[str]]:
        indexers = await asyncio.to_thread(self.get_list)

        async def fetch_and_map(indexer_id: str) -> list[IndexerTorrent]:

            indexer_definition = self._indexer_definitions_service.get_by_id(indexer_id)
            indexer_definition_torrents = (
                await indexer_definition.find_torrents_by_imdb_id(imdb_id)
            )
            return [
                IndexerTorrent(
                    indexer_id=indexer_id,
                    torrent_id=indexer_definition_torrent.torrent_id,
                    download_url=indexer_definition_torrent.download_url,
                    imdb_id=indexer_definition_torrent.imdb_id,
                    seeders=indexer_definition_torrent.seeders,
                    fallback_attributes=indexer_definition_torrent.fallback_attributes,
                )
                for indexer_definition_torrent in indexer_definition_torrents
            ]

        tasks = [fetch_and_map(indexer.id) for indexer in indexers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        indexer_torrents: list[IndexerTorrent] = []
        errors: list[str] = []

        for result in results:
            if isinstance(result, BaseException):
                errors.append(str(result))
            else:
                indexer_torrents.extend(result)

        return indexer_torrents, errors

    async def download_torrent(
        self, indexer_id: str, torrent_id: str, download_url: str
    ) -> DownloadedTorrentFile:
        indexer_definition = self._indexer_definitions_service.get_by_id(indexer_id)
        torrent_bytes = await indexer_definition.download_torrent(download_url)

        return DownloadedTorrentFile(
            indexer_id=indexer_id,
            torrent_id=torrent_id,
            torrent_bytes=torrent_bytes,
        )
