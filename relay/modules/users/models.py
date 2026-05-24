import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from common.database import Base
from common.enums import UserRole
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from modules.users.preferences.models import UserPreferenceModel


class UserModel(Base):
    __tablename__ = "users"

    preferences: Mapped[list["UserPreferenceModel"]] = relationship(
        "UserPreferenceModel",
        back_populates="user",
        cascade="all, delete-orphan",
        init=False,
    )

    username: Mapped[str] = mapped_column(
        sa.String,
        unique=True,
        index=True,
        nullable=False,
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    password_hash: Mapped[str | None] = mapped_column(
        sa.Text,
        default=None,
        nullable=True,
    )

    token: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        index=True,
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        sa.String,
        default=UserRole.USER,
        nullable=False,
    )

    torrent_seed: Mapped[int | None] = mapped_column(
        default=None,
        nullable=True,
    )

    only_best_torrent: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=datetime.now,
        server_default=sa.func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        default=datetime.now,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )
