import uuid

from fastapi import Depends, HTTPException, Request, status
from modules.auth.service import AuthService
from modules.users.dependencies import get_users_service
from modules.users.models import UserModel
from modules.users.service import UsersService


class CurrentUserFetcher:
    def __init__(self, required: bool = True):
        self.required = required

    def __call__(
        self,
        request: Request,
        users_service: UsersService = Depends(get_users_service),
    ) -> UserModel | None:
        user_id_str = request.session.get("user_id")
        if not user_id_str:
            if self.required:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Nincs aktív bejelentkezési munkamenet.",
                )
            return None

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            if self.required:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Érvénytelen munkamenet azonosító.",
                )
            return None

        user = users_service.get_by_id(user_id)
        if not user:
            if self.required:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="A munkamenethez tartozó felhasználó nem található.",
                )
            return None

        return user


def get_auth_service(
    users_service: UsersService = Depends(get_users_service),
) -> AuthService:
    return AuthService(users_service)
