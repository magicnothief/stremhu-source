from common.database import get_db
from fastapi import Depends
from modules.users.repository import UsersRepository
from modules.users.service import UsersService
from sqlalchemy.orm import Session


def get_users_repository(db: Session = Depends(get_db)) -> UsersRepository:
    """FastAPI függőség-injektáló provider a UsersRepository példányosításához."""
    return UsersRepository(db)


def get_users_service(
    users_repository: UsersRepository = Depends(get_users_repository),
) -> UsersService:
    """FastAPI függőség-injektáló provider a UsersService példányosításához."""
    return UsersService(users_repository)
