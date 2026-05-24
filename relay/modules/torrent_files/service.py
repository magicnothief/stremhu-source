import datetime
import logging
from typing import Optional

from fastapi import HTTPException
from modules.libtorrent_client.service import LibtorrentClientService
from modules.torrent_files.models import TorrentFileModel
from modules.torrent_files.repository import TorrentFilesRepository
from modules.torrent_files.schemas import TorrentFilesFilter

logger = logging.getLogger(__name__)


class TorrentFilesService:
    def __init__(
        self,
        repository: TorrentFilesRepository,
        libtorrent_client_service: LibtorrentClientService,
    ):
        self._repository = repository
        self._libtorrent_client_service = libtorrent_client_service

    def create(
        self,
        indexer_id: str,
        torrent_id: str,
        torrent_bytes: bytes,
    ) -> TorrentFileModel:
        """Elmenti a .torrent fájl bájtjait az adatbázisba."""
        torrent_file = self.get_one(
            indexer_id=indexer_id,
            torrent_id=torrent_id,
        )

        if torrent_file:
            raise HTTPException(
                status_code=409,
                detail=f"Már létezik torrent a gyorsítótárban: {indexer_id} - {torrent_id}",
            )

        return self._repository.create(
            TorrentFileModel(
                indexer_id=indexer_id,
                torrent_id=torrent_id,
                torrent_bytes=torrent_bytes,
            )
        )

    def get_one(self, indexer_id: str, torrent_id: str) -> TorrentFileModel | None:
        return self._repository.find_one(
            indexer_id=indexer_id,
            torrent_id=torrent_id,
        )

    def get_one_or_raise(self, indexer_id: str, torrent_id: str) -> TorrentFileModel:
        record = self.get_one(indexer_id, torrent_id)
        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"Nincs ilyen torrent a gyorsítótárban: {indexer_id} - {torrent_id}",
            )
        return record

    def delete(self, indexer_id: str, torrent_id: str) -> None:
        """Töröl egy konkrét gyorsítótárazott .torrent rekordot az adatbázisból."""
        record = self._repository.find_one(
            indexer_id=indexer_id,
            torrent_id=torrent_id,
        )
        if record:
            try:
                self._repository.delete(record)
                logger.info(
                    f"🧹 Torrent fájl törölve az adatbázisból: {indexer_id} - {torrent_id}"
                )
            except Exception as e:
                logger.error(
                    f"Hiba történt a(z) {indexer_id} - {torrent_id} rekord törlése során: {e}"
                )

    def delete_all_by_indexer(self, indexer_id: str) -> None:
        """Törli az indexer összes inaktív .torrent rekordját az adatbázisból."""
        records = self._repository.find_all(
            TorrentFilesFilter(
                indexer_id=indexer_id,
            )
        )
        if not records:
            return

        active_torrents = self._libtorrent_client_service.get_torrents()
        active_hashes = {str(th.info_hash()) for th in active_torrents}

        for record in records:
            info_hash = record.info_hash
            if not info_hash or info_hash not in active_hashes:
                try:
                    self._repository.delete(record)
                except Exception as e:
                    logger.error(
                        f"Nem sikerült törölni a(z) {record.indexer_id} - {record.torrent_id} rekordot: {e}"
                    )

    def run_retention_cleanup(self, retention_seconds: Optional[int] = None) -> None:
        """Törli a gyorsítótárból (adatbázisból) a lejárt és inaktív torrent rekordokat (LRU).

        Ha retention_seconds = 0, minden inaktív torrentet töröl.
        """
        if retention_seconds is None:
            retention_seconds = 7 * 24 * 3600

        now = datetime.datetime.now()
        active_torrents = self._libtorrent_client_service.get_torrents()
        active_hashes = {str(th.info_hash()) for th in active_torrents}

        records = self._repository.find_all()

        for record in records:
            elapsed_seconds = (now - record.last_used_at).total_seconds()
            is_expired = elapsed_seconds > retention_seconds

            info_hash = record.info_hash
            is_active = info_hash is not None and info_hash in active_hashes

            if not is_active and is_expired:
                try:
                    self._repository.delete(record)
                    logger.info(
                        f"🧹 Inaktív, elavult torrent gyorsítótár rekord törölve a DB-ből: {record.indexer_id} - {record.torrent_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Nem sikerült törölni a(z) {record.indexer_id} - {record.torrent_id} elavult rekordot: {e}"
                    )
