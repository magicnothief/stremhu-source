from modules.indexers.models import IndexerModel
from sqlalchemy.orm import Session


class IndexersRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, model: IndexerModel) -> IndexerModel:
        self.db.add(model)
        self.db.flush()

        return model

    def find_all(self) -> list[IndexerModel]:
        return self.db.query(IndexerModel).all()

    def find_by_id(self, id: str) -> IndexerModel | None:
        return self.db.query(IndexerModel).filter_by(id=id).first()
