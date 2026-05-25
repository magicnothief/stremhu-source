from common.enums import UserRole
from fastapi import Depends, HTTPException, status
from modules.auth.dependencies import CurrentUserFetcher
from modules.users.models import UserModel


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    # Beadjuk neki dependency-ként a kötelező user fetchert:
    def __call__(
        self, current_user: UserModel = Depends(CurrentUserFetcher(required=True))
    ):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nincs jogosultságod a művelet végrehajtásához.",
            )
        return current_user
