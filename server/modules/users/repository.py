from modules.users.models import UserModel
from sqlalchemy.orm import Session


class UsersRepository:
    def __init__(self, db: Session):
        self.db = db

    def find(self) -> list[UserModel]:
        return self.db.query(UserModel).all()

    def find_by_id(self, id: str) -> UserModel | None:
        return self.db.query(UserModel).filter_by(id=id).first()

    def find_by_username(self, username: str) -> UserModel | None:
        return self.db.query(UserModel).filter_by(username=username).first()

    def find_by_token(self, token: str) -> UserModel | None:
        return self.db.query(UserModel).filter_by(token=token).first()

    def count(self) -> int:
        return self.db.query(UserModel).count()

    def create(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.flush()

        return user

    def delete(self, user_id: str) -> None:
        self.db.query(UserModel).filter_by(id=user_id).delete()
