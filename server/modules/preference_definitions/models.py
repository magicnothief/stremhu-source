import uuid
from typing import TYPE_CHECKING

from common.database import Base
from modules.preferences.enums import PreferenceEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from modules.preference_definitions.attributes.models import (
        PreferenceDefinitionAttributeModel,
    )


class PreferenceDefinitionModel(Base):
    """
    Database table storing the supported preference categories (definitions).
    E.g., id='resolution', name='resolution'
    """

    __tablename__ = "preference_definitions"

    preference_id: Mapped[PreferenceEnum] = mapped_column(
        String,
        nullable=False,
    )

    # 1-to-many relationship with all preference attributes
    attributes: Mapped[list["PreferenceDefinitionAttributeModel"]] = relationship(
        "PreferenceDefinitionAttributeModel",
        back_populates="definition",
        cascade="all, delete-orphan",
    )

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
