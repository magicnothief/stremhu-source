from modules.persisted_torrents.models import PersistedTorrentModel
from sqlalchemy.orm import Session


class TorrentRepository:
    def __init__(self, db: Session):
        self.db = db

    def find(self) -> list[PersistedTorrentModel]:
        return self.db.query(PersistedTorrentModel).all()

    def find_by_id(
        self, indexer_id: str, torrent_id: str
    ) -> PersistedTorrentModel | None:
        return (
            self.db.query(PersistedTorrentModel)
            .filter_by(indexer_id=indexer_id, torrent_id=torrent_id)
            .first()
        )

    def create(self, persisted_torrent: PersistedTorrentModel) -> PersistedTorrentModel:
        self.db.add(persisted_torrent)
        self.db.flush()

        return persisted_torrent

    def find_by_info_hash(self, info_hash: str) -> PersistedTorrentModel | None:
        return (
            self.db.query(PersistedTorrentModel).filter_by(info_hash=info_hash).first()
        )

    def update(self, persisted_torrent: PersistedTorrentModel) -> PersistedTorrentModel:
        self.db.add(persisted_torrent)
        self.db.flush()

        return persisted_torrent

    def delete(self, info_hash: str) -> None:
        self.db.query(PersistedTorrentModel).filter_by(info_hash=info_hash).delete()
