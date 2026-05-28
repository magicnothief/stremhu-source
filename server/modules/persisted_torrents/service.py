import logging

import libtorrent as libtorrent
from common.constants import PRIO_0, PRIO_1
from fastapi import HTTPException
from modules.indexers.service import IndexersService
from modules.persisted_torrents.models import PersistedTorrentModel
from modules.persisted_torrents.repository import TorrentRepository
from modules.persisted_torrents.schemas import TorrentUpdate
from modules.relay.schemas import RelayTorrent
from modules.relay.service import RelayService
from modules.torrent_files.models import TorrentFileModel
from modules.torrent_files.service import TorrentFilesService

logger = logging.getLogger(__name__)


class TorrentsService:
    def __init__(
        self,
        torrent_repository: TorrentRepository,
        torrent_files_service: TorrentFilesService,
        indexers_service: IndexersService,
        relay_service: RelayService,
    ):
        self._torrent_repository = torrent_repository
        self._torrent_files_service = torrent_files_service
        self._indexers_service = indexers_service
        self._relay_service = relay_service

    def get_torrents(self) -> list[tuple[PersistedTorrentModel, RelayTorrent]]:
        torrents = self._torrent_repository.find()
        relay_torrents = self._relay_service.get_torrents()

        relay_torrent_map = {
            relay_torrent.info_hash: relay_torrent for relay_torrent in relay_torrents
        }

        result: list[tuple[PersistedTorrentModel, RelayTorrent]] = []
        for torrent in torrents:
            if torrent.torrent_file and torrent.torrent_file.info_hash:
                info_hash = torrent.torrent_file.info_hash
                if info_hash in relay_torrent_map:
                    result.append((torrent, relay_torrent_map[info_hash]))

        return result

    async def create(
        self,
        indexer_id: str,
        torrent_id: str,
    ) -> tuple[PersistedTorrentModel, RelayTorrent]:
        existing_torrent = self._torrent_repository.find_by_id(
            indexer_id=indexer_id,
            torrent_id=torrent_id,
        )
        if existing_torrent:
            raise HTTPException(409, "A torrent már létezik.")

        torrent_file = self._torrent_files_service.get_one(
            indexer_id=indexer_id,
            torrent_id=torrent_id,
        )

        if torrent_file is None:
            indexer_torrent = await self._indexers_service.get_torrent_by_torrent_id(
                indexer_id=indexer_id, torrent_id=torrent_id
            )
            downloaded_torrent_file = await self._indexers_service.download_torrent(
                indexer_id=indexer_id,
                torrent_id=torrent_id,
                download_url=indexer_torrent.download_url,
            )
            torrent_file = self._torrent_files_service.create(
                indexer_id=indexer_id,
                torrent_id=torrent_id,
                torrent_bytes=downloaded_torrent_file.torrent_bytes,
            )

        info_hash = torrent_file.info.info_hash

        torrent_model = PersistedTorrentModel(
            indexer_id=indexer_id,
            torrent_id=torrent_id,
            info_hash=info_hash,
        )

        torrent = self._torrent_repository.create(torrent_model)
        relay_torrent = self._relay_service.add_torrent(
            torrent_bytes=torrent.torrent_file.torrent_bytes,
        )

        return torrent, relay_torrent

    def create_from_torrent_file(
        self, torrent_file: TorrentFileModel
    ) -> tuple[PersistedTorrentModel, RelayTorrent]:
        torrent_model = PersistedTorrentModel(
            indexer_id=torrent_file.indexer_id,
            torrent_id=torrent_file.torrent_id,
            info_hash=torrent_file.info.info_hash,
        )

        torrent = self._torrent_repository.create(torrent_model)
        relay_torrent = self._relay_service.add_torrent(
            torrent_bytes=torrent.torrent_file.torrent_bytes,
        )

        return torrent, relay_torrent

    def get_one(
        self,
        indexer_id: str,
        torrent_id: str,
    ) -> tuple[PersistedTorrentModel, RelayTorrent] | None:
        torrent = self._torrent_repository.find_by_id(
            indexer_id=indexer_id,
            torrent_id=torrent_id,
        )
        if torrent is None:
            return None

        relay_torrent = self._relay_service.get_torrent_or_raise(torrent.info_hash)
        return torrent, relay_torrent

    def get_or_raise(
        self,
        info_hash: str,
    ) -> tuple[PersistedTorrentModel, RelayTorrent]:
        torrent = self._torrent_repository.find_by_info_hash(info_hash)
        if torrent is None:
            raise HTTPException(404, "A torrent nem található")

        relay_torrent = self._relay_service.get_torrent_or_raise(info_hash)

        return torrent, relay_torrent

    def update(
        self,
        info_hash: str,
        payload: TorrentUpdate,
    ) -> tuple[PersistedTorrentModel, RelayTorrent]:
        persisted = self._torrent_repository.find_by_info_hash(info_hash)
        if persisted is None:
            raise HTTPException(404, "A torrent nem található")

        if payload.is_persisted is not None:
            persisted.is_persisted = payload.is_persisted

        if payload.download_full_torrent is not None:
            persisted.full_download = payload.download_full_torrent

            priority = PRIO_1 if payload.download_full_torrent else PRIO_0
            sha1_hash = self.parse_info_hash(info_hash)
            torrent = self._relay_service._torrents.get(sha1_hash)
            if torrent:
                torrent.update_default_priorities(priority)

        self._torrent_repository.update(persisted)

        relay_torrent = self._relay_service.get_torrent_or_raise(info_hash)
        return persisted, relay_torrent

    def delete(
        self,
        info_hash: str,
    ):
        self._torrent_repository.delete(info_hash=info_hash)
        self._relay_service.delete_torrent(info_hash=info_hash)

    def parse_info_hash(self, info_hash_str: str) -> libtorrent.sha1_hash:
        sha1_hash = libtorrent.sha1_hash(bytes.fromhex(info_hash_str))
        return sha1_hash

    def save_resume_data(self, info_hash: str, resume_bytes: bytes) -> None:
        persisted = self._torrent_repository.find_by_info_hash(info_hash)
        if persisted:
            persisted.resume_bytes = resume_bytes
            self._torrent_repository.update(persisted)
