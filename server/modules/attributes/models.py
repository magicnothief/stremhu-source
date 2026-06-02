import sqlalchemy as sa
from common.database import Base
from modules.preferences.models import PreferenceModel
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AttributeModel(Base):
    __tablename__ = "attributes"

    id: Mapped[str] = mapped_column(sa.String, primary_key=True)

    name: Mapped[str] = mapped_column(sa.String)

    preference_id: Mapped[str | None] = mapped_column(
        sa.ForeignKey("preferences.id", ondelete="CASCADE"),
    )

    preference: Mapped[PreferenceModel | None] = relationship(
        "PreferenceModel",
        back_populates="attributes",
        init=False,
    )

    pattern: Mapped[str | None] = mapped_column(
        sa.String,
        default=None,
    )
