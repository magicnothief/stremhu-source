import sqlalchemy as sa
from common.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class SettingModel(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(sa.String, primary_key=True)
    value: Mapped[dict] = mapped_column(sa.JSON, default=dict)
