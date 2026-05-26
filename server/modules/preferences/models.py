import sqlalchemy as sa
from common.database import Base
from modules.preferences.enums import PreferenceEnum
from sqlalchemy.orm import Mapped, mapped_column


class PreferenceModel(Base):
    __tablename__ = "preferences"

    id: Mapped[PreferenceEnum] = mapped_column(sa.String, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String)
    description: Mapped[str] = mapped_column(sa.String)
