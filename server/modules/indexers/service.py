import asyncio
import logging

from fastapi import HTTPException, status
from modules.indexer_accounts.models import IndexerAccountModel
from modules.indexer_accounts.schemas import IndexerAccountCreate
from modules.indexer_accounts.service import IndexerAccountsService
from modules.indexer_definitions.exceptions import (
    AuthenticationException,
    CredentialsRequiredException,
)
from modules.indexer_definitions.schemas import IndexerDefinitionLogin
from modules.indexer_definitions.service import IndexerDefinitionsService
from modules.indexers.schemas import DownloadedTorrentFile, IndexerLogin, IndexerTorrent
from modules.torrents.service import TorrentsService

logger = logging.getLogger(__name__)


class IndexersService:
    def __init__(
        self,
        indexer_definitions_service: IndexerDefinitionsService,
        indexer_accounts_service: IndexerAccountsService,
        torrents_service: TorrentsService,
    ):
        self._indexer_definitions_service = indexer_definitions_service
        self._indexer_accounts_service = indexer_accounts_service
        self._torrents_service = torrents_service

    async def login(self, payload: IndexerLogin) -> IndexerAccountModel:
        indexer_definition = self._indexer_definitions_service.get_by_id(
            payload.indexer_id
        )
        indexer_account = await asyncio.to_thread(
            self._indexer_accounts_service.get_by_id, indexer_definition.id
        )

        if indexer_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A megadott '{indexer_definition.name}' már be van jelentkezve!",
            )

        try:
            await indexer_definition.login(
                IndexerDefinitionLogin(
                    username=payload.username,
                    password=payload.password,
                )
            )

            return await asyncio.to_thread(
                self._indexer_accounts_service.create,
                IndexerAccountCreate(
                    indexer_definition_id=indexer_definition.id,
                    username=payload.username,
                    password=payload.password,
                    download_full_torrent=indexer_definition.requires_full_download,
                ),
            )
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

    async def get_torrents_by_torrent_id(
        self, torrent_id: str
    ) -> tuple[list[IndexerTorrent], list[str]]:
        indexer_accounts = await asyncio.to_thread(
            self._indexer_accounts_service.get_list
        )

        async def fetch_and_map(indexer_account: IndexerAccountModel) -> IndexerTorrent:
            indexer_definition = self._indexer_definitions_service.get_by_id(
                indexer_account.indexer_id
            )
            indexer_definition_torrent = await indexer_definition.find_torrent_by_id(
                torrent_id
            )
            return IndexerTorrent(
                indexer_account=indexer_account,
                torrent_id=indexer_definition_torrent.torrent_id,
                download_url=indexer_definition_torrent.download_url,
                imdb_id=indexer_definition_torrent.imdb_id,
                seeders=indexer_definition_torrent.seeders,
                fallback_attributes=indexer_definition_torrent.fallback_attributes,
            )

        tasks = [fetch_and_map(indexer_account) for indexer_account in indexer_accounts]
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
        indexer_account = await asyncio.to_thread(
            self._indexer_accounts_service.get_by_id_or_raise, indexer_id
        )

        indexer_definition = self._indexer_definitions_service.get_by_id(
            indexer_account.indexer_id
        )
        indexer_definition_torrent = await indexer_definition.find_torrent_by_id(
            torrent_id
        )
        return IndexerTorrent(
            indexer_account=indexer_account,
            torrent_id=indexer_definition_torrent.torrent_id,
            download_url=indexer_definition_torrent.download_url,
            imdb_id=indexer_definition_torrent.imdb_id,
            seeders=indexer_definition_torrent.seeders,
            fallback_attributes=indexer_definition_torrent.fallback_attributes,
        )

    async def get_torrents_by_imdb_id(
        self, imdb_id: str
    ) -> tuple[list[IndexerTorrent], list[str]]:
        indexer_accounts = await asyncio.to_thread(
            self._indexer_accounts_service.get_list
        )

        async def fetch_and_map(
            indexer_account: IndexerAccountModel,
        ) -> list[IndexerTorrent]:

            indexer_definition = self._indexer_definitions_service.get_by_id(
                indexer_account.indexer_id
            )
            indexer_definition_torrents = (
                await indexer_definition.find_torrents_by_imdb_id(imdb_id)
            )
            return [
                IndexerTorrent(
                    indexer_account=indexer_account,
                    torrent_id=indexer_definition_torrent.torrent_id,
                    download_url=indexer_definition_torrent.download_url,
                    imdb_id=indexer_definition_torrent.imdb_id,
                    seeders=indexer_definition_torrent.seeders,
                    fallback_attributes=indexer_definition_torrent.fallback_attributes,
                )
                for indexer_definition_torrent in indexer_definition_torrents
            ]

        tasks = [fetch_and_map(indexer_account) for indexer_account in indexer_accounts]
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
        indexer_account = await asyncio.to_thread(
            self._indexer_accounts_service.get_by_id_or_raise, indexer_id
        )

        indexer_definition = self._indexer_definitions_service.get_by_id(
            indexer_account.indexer_id
        )
        torrent_bytes = await indexer_definition.download_torrent(download_url)

        return DownloadedTorrentFile(
            indexer_account=indexer_account,
            torrent_id=torrent_id,
            torrent_bytes=torrent_bytes,
        )
