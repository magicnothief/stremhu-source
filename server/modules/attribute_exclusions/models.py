from typing import TYPE_CHECKING
from uuid import uuid4

import sqlalchemy as sa
from common.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from modules.attributes.models import AttributeModel


class AttributeExclusionModel(Base):
    __tablename__ = "attribute_exclusions"

    __table_args__ = (
        sa.Index(
            "uq_attribute_exclusions_user",
            "attribute_id",
            "user_id",
            unique=True,
            sqlite_where=sa.text("user_id IS NOT NULL"),
        ),
        sa.Index(
            "uq_attribute_exclusions_system",
            "attribute_id",
            unique=True,
            sqlite_where=sa.text("user_id IS NULL"),
        ),
    )

    attribute_id: Mapped[str] = mapped_column(
        sa.ForeignKey("attributes.id", ondelete="CASCADE"),
        index=True,
    )

    attribute: Mapped["AttributeModel"] = relationship(
        "AttributeModel",
        uselist=False,
        init=False,
    )

    user_id: Mapped[str | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    id: Mapped[str] = mapped_column(
        sa.String,
        primary_key=True,
        default_factory=lambda: str(uuid4()),
    )
