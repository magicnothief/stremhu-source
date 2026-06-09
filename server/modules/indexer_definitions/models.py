import sqlalchemy as sa
from modules.attributes.models import AttributeModel
from sqlalchemy.orm import Mapped, mapped_column


class IndexerDefinitionModel(AttributeModel):
    """Database representation of static tracker integrations discovered at runtime"""

    __tablename__ = "indexer_definitions"

    id: Mapped[str] = mapped_column(
        sa.ForeignKey("attributes.id", ondelete="CASCADE"),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        sa.String,
    )

    url: Mapped[str] = mapped_column(
        sa.String,
    )

    details_path: Mapped[str] = mapped_column(
        sa.String,
    )

    requires_full_download: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
    )

    __mapper_args__ = {
        "polymorphic_identity": "indexer_definition",
    }
