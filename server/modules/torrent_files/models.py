import datetime
from dataclasses import field

import sqlalchemy as sa
from common.database import Base
from modules.persisted_torrents.models import PersistedTorrentModel
from modules.torrent_files.exceptions import InvalidTorrentFileException
from modules.torrent_files.schemas import TorrentFileInfo, TorrentInfo
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from torf import Torrent as TorfTorrent


class TorrentFileModel(Base):
    __tablename__ = "torrent_files"

    indexer_id: Mapped[str] = mapped_column(sa.String, primary_key=True)
    torrent_id: Mapped[str] = mapped_column(sa.String, primary_key=True)
    info_hash: Mapped[str] = mapped_column(
        sa.String,
        index=True,
        init=False,
    )
    torrent_bytes: Mapped[bytes] = mapped_column(sa.LargeBinary)

    last_used_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        default_factory=datetime.datetime.now,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        default_factory=datetime.datetime.now,
    )

    persisted_torrent: Mapped[PersistedTorrentModel | None] = relationship(
        "PersistedTorrentModel",
        back_populates="torrent_file",
        uselist=False,
        init=False,
    )

    _cached_info: TorrentInfo | None = field(default=None, init=False, repr=False)

    @validates("torrent_bytes")
    def validate_torrent_bytes(self, _: str, value: bytes) -> bytes:
        self._cached_info = self._torrent_info(value)
        self.info_hash = self._cached_info.info_hash
        return value

    @property
    def info(self) -> TorrentInfo:
        if self._cached_info is None:
            self._cached_info = self._torrent_info(self.torrent_bytes)
        return self._cached_info

    def _torrent_info(self, torrent_bytes: bytes) -> TorrentInfo:
        try:
            torrent = TorfTorrent.read_stream(torrent_bytes)
            torrent.validate()

            files = [
                TorrentFileInfo(name=str(file), index=index, size=file.size)
                for index, file in enumerate(torrent.files)
            ]

            return TorrentInfo(
                info_hash=torrent.infohash,
                name=torrent.name or "",
                size=torrent.size,
                files=files,
            )
        except Exception:
            raise InvalidTorrentFileException()
