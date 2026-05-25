import uuid

from argon2 import PasswordHasher
from fastapi import HTTPException, status
from modules.users.models import UserModel
from modules.users.repository import UsersRepository
from modules.users.schemas import CreateUser, UpdateUser


class UsersService:
    def __init__(self, users_repository: UsersRepository):
        self._users_repository = users_repository

    def get_by_id(self, user_id: str) -> UserModel | None:
        return self._users_repository.find_by_id(user_id)

    def get_by_username(self, username: str) -> UserModel | None:
        return self._users_repository.find_by_username(username)

    def get_by_token(self, token: str) -> UserModel | None:
        return self._users_repository.find_by_token(token)

    def count(self) -> int:
        return self._users_repository.count()

    def create(self, payload: CreateUser) -> UserModel:
        existing_user = self._users_repository.find_by_username(payload.username)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ez a felhasználónév már foglalt.",
            )

        password_hash = self._hash_password(payload.password)

        user = UserModel(
            username=payload.username,
            password_hash=password_hash,
            role=payload.role,
            token=str(uuid.uuid4()),
            torrent_seed=payload.torrent_seed,
            only_best_torrent=payload.only_best_torrent,
        )

        return self._users_repository.create(user)

    def update(self, user_id: str, payload: UpdateUser) -> UserModel:
        user = self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A felhasználó nem található.",
            )

        update_data = payload.model_dump(exclude_unset=True)

        if "password" in update_data:
            password = update_data.pop("password")
            if password is not None:
                user.password_hash = self._hash_password(password)
            else:
                user.password_hash = None

        for key, value in update_data.items():
            setattr(user, key, value)

        return self._users_repository.create(user)

    def _hash_password(self, password: str) -> str:
        ph = PasswordHasher()
        return ph.hash(password)
