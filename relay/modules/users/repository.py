import uuid

from modules.users.models import UserModel
from sqlalchemy.orm import Session


class UsersRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        return self.db.query(UserModel).filter_by(id=user_id).first()

    def find_by_username(self, username: str) -> UserModel | None:
        return self.db.query(UserModel).filter_by(username=username).first()

    def count(self) -> int:
        return self.db.query(UserModel).count()

    def create(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.flush()

        return user
