import sqlalchemy as sa
from common.database import Base
from modules.preferences.models import PreferenceModel
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AttributeModel(Base):
    __tablename__ = "attributes"
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "base",
    }

    id: Mapped[str] = mapped_column(sa.String, primary_key=True)

    type: Mapped[str] = mapped_column(sa.String, init=False)

    preference_id: Mapped[str | None] = mapped_column(
        sa.ForeignKey("preferences.id", ondelete="CASCADE"),
    )

    preference: Mapped["PreferenceModel | None"] = relationship(
        "PreferenceModel",
        back_populates="attributes",
        init=False,
    )
