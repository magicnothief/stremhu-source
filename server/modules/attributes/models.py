import sqlalchemy as sa
from common.database import Base
from modules.preferences.enums import PreferenceEnum
from sqlalchemy.orm import Mapped, mapped_column


class AttributeModel(Base):
    __tablename__ = "attributes"

    id: Mapped[str] = mapped_column(sa.String, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    preference_id: Mapped[PreferenceEnum | None] = mapped_column(
        sa.ForeignKey("preferences.id", ondelete="CASCADE"),
        nullable=True,
    )
