from common.database import get_db
from fastapi import Depends
from modules.users.repository import UsersRepository
from modules.users.service import UsersService
from sqlalchemy.orm import Session


def create_users_service(db: Session) -> UsersService:
    """Hozzárendeli a szervizt egy háttérfeladat vagy HTTP kérés adatbázis munkamenetéhez."""
    users_repository = UsersRepository(db)
    return UsersService(users_repository)


def get_users_service(
    db: Session = Depends(get_db),
) -> UsersService:
    """FastAPI függőség-injektáló provider a UsersService példányosításához."""
    return create_users_service(db)
