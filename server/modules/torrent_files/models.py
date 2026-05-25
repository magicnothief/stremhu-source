import datetime
from dataclasses import field

import sqlalchemy as sa
from common.database import Base
from modules.persisted_torrents.models import PersistedTorrentModel
from modules.torrent_files.exceptions import InvalidTorrentFileException
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
        default=datetime.datetime.now,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        default=datetime.datetime.now,
    )

    persisted_torrent: Mapped[PersistedTorrentModel | None] = relationship(
        "PersistedTorrentModel",
        back_populates="torrent_file",
        uselist=False,
        init=False,
    )

    _cached_info: TorfTorrent | None = field(default=None, init=False, repr=False)

    @validates("torrent_bytes")
    def validate_torrent_bytes(self, _: str, value: bytes) -> bytes:
        try:
            torrent = TorfTorrent.read_stream(value)
            torrent.validate()

            self._cached_info = torrent
            self.info_hash = torrent.infohash
        except Exception:
            raise InvalidTorrentFileException()
        return value

    @property
    def info(self) -> TorfTorrent:
        if self._cached_info is None:
            try:
                self._cached_info = TorfTorrent.read_stream(self.torrent_bytes)
            except Exception:
                raise InvalidTorrentFileException()
        return self._cached_info
