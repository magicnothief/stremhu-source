import datetime
from sqlite3 import Date

import sqlalchemy as sa
from common.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class IndexerModel(Base):
    __tablename__ = "indexers"

    id: Mapped[str] = mapped_column(sa.String, primary_key=True)

    username: Mapped[str] = mapped_column(sa.String)

    password: Mapped[str] = mapped_column(sa.String)

    hit_and_run: Mapped[bool | None] = mapped_column(sa.Boolean, default=None)

    keep_seed_seconds: Mapped[int | None] = mapped_column(sa.Integer, default=None)

    download_full_torrent: Mapped[bool] = mapped_column(sa.Boolean, default=False)

    updated_at: Mapped[Date] = mapped_column(
        sa.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    created_at: Mapped[Date] = mapped_column(
        sa.DateTime,
        default=datetime.datetime.now,
    )
