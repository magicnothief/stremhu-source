from typing import Annotated

from modules.settings.schemas.internal import (
    NetworkAutoSettings,
    NetworkLocalSettings,
    NetworkManualSettings,
    RelaySettings,
    RelaySettingsUpdate,
    SystemSettingsUpdate,
)
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SystemSettingsResponse(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    hit_and_run: bool
    keep_seed_seconds: int
    cache_retention_seconds: int


class SystemSettingsUpdateRequest(SystemSettingsUpdate):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class RelaySettingsResponse(RelaySettings):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class RelaySettingsUpdateRequest(RelaySettingsUpdate):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class NetworkLocalSettingsResponse(NetworkLocalSettings):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class NetworkAutoSettingsResponse(NetworkAutoSettings):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class NetworkManualSettingsResponse(NetworkManualSettings):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


NetworkSettingsResponse = Annotated[
    NetworkLocalSettingsResponse
    | NetworkAutoSettingsResponse
    | NetworkManualSettingsResponse,
    Field(discriminator="mode"),
]
