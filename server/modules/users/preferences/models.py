import uuid
from typing import TYPE_CHECKING

from common.database import Base
from modules.preference_definitions.models import PreferenceDefinitionModel
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from modules.users.models import UserModel


class UserPreferenceModel(Base):
    """
    User preference overrides representing the category priority order.
    Individual choices (preferred/blocked values) live in the preference_items table.
    """

    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="preferences",
    )

    definition_id: Mapped[str] = mapped_column(
        ForeignKey("preference_definitions.id", ondelete="CASCADE"),
        nullable=False,
    )

    definition: Mapped["PreferenceDefinitionModel"] = relationship(
        "PreferenceDefinitionModel",
    )

    order: Mapped[int] = mapped_column(Integer, nullable=False)

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
    )
