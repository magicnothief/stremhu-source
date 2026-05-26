import sqlalchemy as sa
from common.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class IndexerDefinitionModel(Base):
    """Database representation of static tracker integrations discovered at runtime"""

    __tablename__ = "indexer_definitions"

    id: Mapped[str] = mapped_column(sa.String, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    url: Mapped[str] = mapped_column(sa.String, nullable=False)
    details_path: Mapped[str] = mapped_column(sa.String, nullable=False)
    requires_full_download: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False
    )
