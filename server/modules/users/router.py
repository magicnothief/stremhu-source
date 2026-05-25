from common.enums import UserRole
from fastapi import APIRouter, Depends, status
from modules.auth.dependencies import SessionGuard
from modules.users.dependencies import get_users_service
from modules.users.models import UserModel
from modules.users.schemas import CreateUser, UpdateUser, User
from modules.users.service import UsersService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: CreateUser,
    users_service: UsersService = Depends(get_users_service),
    current_user: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> User:
    new_user = users_service.create(payload)
    return User.model_validate(new_user)


@router.put(
    "/{user_id}",
    response_model=User,
)
def update(
    user_id: str,
    payload: UpdateUser,
    users_service: UsersService = Depends(get_users_service),
    current_user: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> User:
    updated_user = users_service.update(user_id, payload)
    return User.model_validate(updated_user)
