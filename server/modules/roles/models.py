import sqlalchemy as sa
from common.database import Base
from modules.roles.enums import UserRole
from sqlalchemy.orm import Mapped, mapped_column


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[UserRole] = mapped_column(sa.String, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String)
