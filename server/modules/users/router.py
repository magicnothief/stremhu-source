from fastapi import APIRouter, Depends, status
from modules.auth.dependencies import SessionGuard
from modules.roles.enums import UserRole
from modules.users.dependencies import get_users_service
from modules.users.models import UserModel
from modules.users.schemas import CreateUser, UpdateUser, User
from modules.users.service import UsersService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[User],
)
def find(
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> list[UserModel]:
    return users_service.get_list()


@router.get(
    "/{user_id}",
    response_model=User,
)
def find_by_id(
    user_id: str,
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> UserModel:
    return users_service.get_by_id_or_raise(user_id)


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: CreateUser,
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> UserModel:
    return users_service.create(payload)


@router.put(
    "/{user_id}",
    response_model=User,
)
def update(
    user_id: str,
    payload: UpdateUser,
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> UserModel:
    return users_service.update(user_id, payload)


@router.put(
    "/{user_id}/token/regenerate",
    response_model=User,
)
def regenerate_token(
    user_id: str,
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> UserModel:
    return users_service.regenerate_token(user_id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    user_id: str,
    users_service: UsersService = Depends(get_users_service),
    current_user: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> None:
    users_service.delete(user_id, current_user)
