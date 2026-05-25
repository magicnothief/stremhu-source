from datetime import datetime

from common.enums import UserRole
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseUser(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    username: str
    role: UserRole = UserRole.USER
    torrent_seed: int | None = None
    only_best_torrent: bool = False


class CreateUser(BaseUser):
    password: str


class UpdateUser(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    username: str | None = None
    password: str | None = None
    role: UserRole | None = None
    torrent_seed: int | None = None
    only_best_torrent: bool | None = None


class User(BaseUser):
    id: str
    token: str
    updated_at: datetime
    created_at: datetime
