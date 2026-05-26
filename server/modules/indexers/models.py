import datetime
from sqlite3 import Date

import sqlalchemy as sa
from common.database import Base
from modules.indexers.definitions.models import IndexerDefinitionModel
from sqlalchemy.orm import Mapped, mapped_column, relationship


class IndexerModel(Base):
    __tablename__ = "indexers"

    id: Mapped[str] = mapped_column(
        sa.ForeignKey("indexer_definitions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    definition: Mapped["IndexerDefinitionModel"] = relationship(
        "IndexerDefinitionModel",
        init=False,
    )

    username: Mapped[str] = mapped_column(sa.String)

    password: Mapped[str] = mapped_column(sa.String)

    hit_and_run: Mapped[bool | None] = mapped_column(sa.Boolean, default=None)

    keep_seed_seconds: Mapped[int | None] = mapped_column(sa.Integer, default=None)

    download_full_torrent: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    updated_at: Mapped[Date] = mapped_column(
        sa.DateTime,
        default_factory=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    created_at: Mapped[Date] = mapped_column(
        sa.DateTime,
        default_factory=datetime.datetime.now,
    )
