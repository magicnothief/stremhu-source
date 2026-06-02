from modules.users.schemas.internal import (
    User,
    UserCreate,
    UserPreferenceCreate,
    UserPreferencesReorder,
    UserPreferenceUpdate,
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


class UserResponse(User):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class UserPreferenceCreateRequest(UserPreferenceCreate):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class UserPreferenceUpdateRequest(UserPreferenceUpdate):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class UserPreferencesReorderRequest(UserPreferencesReorder):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )
