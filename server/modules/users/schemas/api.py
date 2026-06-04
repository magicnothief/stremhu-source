from datetime import datetime

from modules.roles.schemas.api import RoleResponse
from modules.users.schemas.internal import (
    BaseUser,
    UserCreate,
    UserUpdate,
)
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class UserCreateRequest(UserCreate):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class UserUpdateRequest(UserUpdate):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class UserResponse(BaseUser):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    id: str
    role: RoleResponse
    api_key: str
    updated_at: datetime
    created_at: datetime
