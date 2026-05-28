from modules.preferences.enums import PreferenceEnum
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class UpdateMe(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    username: str | None = None
    password: str | None = None
    torrent_seed: int | None = None
    only_best_torrent: bool | None = None


class UserPreferenceCreate(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    preference: PreferenceEnum
    preferred: list[str]


class UserPreferenceUpdate(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    preferred: list[str]


class ReorderPreferences(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    preferences: list[PreferenceEnum]
