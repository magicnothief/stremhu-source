from modules.attributes.models import AttributeModel
from modules.preferences.enums import PreferenceEnum
from sqlalchemy.orm import Session


class AttributesRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[AttributeModel]:
        """Fetches all attributes from the database."""
        return self.db.query(AttributeModel).all()

    def find_by_preference(self, preference: PreferenceEnum) -> list[AttributeModel]:
        """Fetches all attributes belonging to a specific preference category."""
        return (
            self.db.query(AttributeModel)
            .filter(AttributeModel.preference_id == preference)
            .all()
        )

    def find_by_id(self, attribute_id: str) -> AttributeModel | None:
        """Finds a single attribute by its ID."""
        return (
            self.db.query(AttributeModel)
            .filter(AttributeModel.id == attribute_id)
            .first()
        )

    def add(self, attribute: AttributeModel) -> None:
        """Adds a new attribute entity to the session."""
        self.db.add(attribute)

    def delete_excluding_ids(self, exclude_ids: set[str]) -> int:
        """Deletes all attributes whose IDs are not in the provided set."""
        return (
            self.db.query(AttributeModel)
            .filter(AttributeModel.id.not_in(exclude_ids))
            .delete(synchronize_session=False)
        )

    def commit(self) -> None:
        """Commits the active database transaction."""
        self.db.commit()
