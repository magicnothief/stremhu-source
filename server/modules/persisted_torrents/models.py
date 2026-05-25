import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from common.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from modules.torrent_files.models import TorrentFileModel


class PersistedTorrentModel(Base):
    __tablename__ = "persisted_torrents"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["indexer_id", "torrent_id"],
            ["torrent_files.indexer_id", "torrent_files.torrent_id"],
            name="fk_persisted_torrents_torrent_files",
            ondelete="RESTRICT",
        ),
    )

    indexer_id: Mapped[str] = mapped_column(
        sa.String,
        primary_key=True,
    )

    torrent_id: Mapped[str] = mapped_column(
        sa.String,
        primary_key=True,
    )

    last_played_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        default=datetime.datetime.now,
    )

    is_persisted: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    full_download: Mapped[bool | None] = mapped_column(
        sa.Boolean,
        default=None,
    )

    resume_bytes: Mapped[bytes | None] = mapped_column(
        sa.LargeBinary,
        default=None,
    )

    updated_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        default=datetime.datetime.now,
    )

    torrent_file: Mapped["TorrentFileModel"] = relationship(
        "TorrentFileModel",
        back_populates="persisted_torrent",
        init=False,
    )
