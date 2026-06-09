import sqlalchemy as sa
from modules.attributes.models import AttributeModel
from sqlalchemy.orm import Mapped, mapped_column


class MediaAttributeModel(AttributeModel):
    __tablename__ = "media_attributes"
    __mapper_args__ = {
        "polymorphic_identity": "media",
    }

    id: Mapped[str] = mapped_column(
        sa.ForeignKey("attributes.id", ondelete="CASCADE"), primary_key=True
    )

    name: Mapped[str] = mapped_column(sa.String)

    pattern: Mapped[str | None] = mapped_column(
        sa.String,
        default=None,
    )

    short_name: Mapped[str | None] = mapped_column(
        sa.String,
        default=None,
    )
