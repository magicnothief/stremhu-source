import uuid
from datetime import datetime

import sqlalchemy as sa
from common.database import Base, UTCDateTime
from modules.roles.enums import UserRole
from modules.roles.models import RoleModel
from modules.user_preference_definitions.models import UserPreferenceDefinitionModel
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserModel(Base):
    __tablename__ = "users"

    preference_definitions: Mapped[list["UserPreferenceDefinitionModel"]] = (
        relationship(
            "UserPreferenceDefinitionModel",
            back_populates="user",
            cascade="all, delete-orphan",
            init=False,
        )
    )

    username: Mapped[str] = mapped_column(
        sa.String,
        unique=True,
        index=True,
        nullable=False,
    )

    id: Mapped[str] = mapped_column(
        sa.String,
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
    )

    password_hash: Mapped[str | None] = mapped_column(
        sa.Text,
        default=None,
        nullable=True,
    )

    token: Mapped[str] = mapped_column(
        sa.String,
        default_factory=lambda: str(uuid.uuid4()),
        index=True,
        nullable=False,
    )

    role_id: Mapped[UserRole] = mapped_column(
        sa.ForeignKey("roles.id"),
        default=UserRole.USER,
        nullable=False,
    )

    role: Mapped["RoleModel"] = relationship("RoleModel", init=False)

    torrent_seed: Mapped[int | None] = mapped_column(
        default=None,
        nullable=True,
    )

    only_best_torrent: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default_factory=datetime.now,
        server_default=sa.func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        default_factory=datetime.now,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        nullable=False,
    )
