import datetime
import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from common.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from modules.users.models import UserModel


class PairingModel(Base):
    __tablename__ = "pairings"

    expires_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
    )

    user_code: Mapped[str] = mapped_column(
        sa.String,
        index=True,
    )

    device_code: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        index=True,
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    status: Mapped[str] = mapped_column(
        sa.String,
        default="pending",
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        default=None,
    )

    user: Mapped["UserModel | None"] = relationship(
        "UserModel",
        uselist=False,
        init=False,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime,
        default=datetime.datetime.now,
        server_default=sa.func.now(),
        nullable=False,
    )
