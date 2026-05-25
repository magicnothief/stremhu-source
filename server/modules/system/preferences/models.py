import uuid
from typing import TYPE_CHECKING

from common.database import Base
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from modules.preference_definitions.models import PreferenceDefinitionModel


class SystemPreferenceModel(Base):
    """
    Global default priority orders for preference categories.
    E.g., default category order for 'resolution' is 1.
    """

    __tablename__ = "system_preferences"

    definition_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("preference_definitions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    definition: Mapped["PreferenceDefinitionModel"] = relationship(
        "PreferenceDefinitionModel",
    )

    order: Mapped[int] = mapped_column(Integer, nullable=False)
