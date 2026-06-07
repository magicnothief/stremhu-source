from modules.attribute_exclusions.models import AttributeExclusionModel
from modules.attribute_exclusions.schemas.internal import AttributeExclusionCreate
from sqlalchemy.orm import Session


class AttributeExclusionsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        payload: AttributeExclusionCreate,
    ) -> AttributeExclusionModel:
        model = AttributeExclusionModel(**payload.model_dump())

        self.db.add(model)
        self.db.flush()

        return model

    def find_list(self) -> list[AttributeExclusionModel]:
        return self.db.query(AttributeExclusionModel).all()

    def find_by_id(
        self,
        attribute_id: str,
        user_id: str | None,
    ) -> AttributeExclusionModel | None:
        return (
            self.db.query(AttributeExclusionModel)
            .filter_by(attribute_id=attribute_id, user_id=user_id)
            .first()
        )

    def delete(
        self,
        attribute_id: str,
        user_id: str | None,
    ) -> None:
        self.db.query(AttributeExclusionModel).filter_by(
            attribute_id=attribute_id, user_id=user_id
        ).delete()
