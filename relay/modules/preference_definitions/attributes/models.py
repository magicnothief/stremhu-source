import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from common.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from modules.preference_definitions.models import PreferenceDefinitionModel


class PreferenceDefinitionAttributeModel(Base):
    """Definition of a preference option"""

    __tablename__ = "preference_definition_attributes"

    definition_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("preference_definitions.id", ondelete="CASCADE"),
        nullable=False,
    )

    attribute_id: Mapped[str] = mapped_column(
        sa.String,
        nullable=False,
    )

    order: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    definition: Mapped["PreferenceDefinitionModel"] = relationship(
        "PreferenceDefinitionModel",
        back_populates="attributes",
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
