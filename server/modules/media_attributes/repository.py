from modules.media_attributes.models import MediaAttributeModel
from sqlalchemy.orm import Session


class MediaAttributesRepository:
    def __init__(self, db: Session):
        self.db = db

    def delete_excluding_ids(self, ids: set[str]) -> int:
        return (
            self.db.query(MediaAttributeModel)
            .filter(~MediaAttributeModel.id.in_(ids))
            .delete(synchronize_session=False)
        )

    def add(self, attribute: MediaAttributeModel) -> None:
        self.db.add(attribute)
