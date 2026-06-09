import sqlalchemy as sa
from modules.attributes.models import AttributeModel
from sqlalchemy.orm import Mapped, mapped_column


class MediaAttributeModel(AttributeModel, kw_only=True):
    __tablename__ = "media_attributes"
    __mapper_args__ = {
        "polymorphic_identity": "media",
    }

    name: Mapped[str] = mapped_column(sa.String)

    id: Mapped[str] = mapped_column(
        sa.ForeignKey("attributes.id", ondelete="CASCADE"), primary_key=True
    )

    pattern: Mapped[str | None] = mapped_column(
        sa.String,
        default=None,
    )

    short_name: Mapped[str | None] = mapped_column(
        sa.String,
        default=None,
    )
