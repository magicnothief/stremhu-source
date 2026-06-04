from typing import Annotated

from modules.network.schemas.internal import NetworkAutoSetup, NetworkManualSetup
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel


class NetworkAutoSetupRequest(NetworkAutoSetup):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class NetworkManualSetupRequest(NetworkManualSetup):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


NetworkSetupRequest = Annotated[
    NetworkAutoSetupRequest | NetworkManualSetupRequest,
    Field(discriminator="mode"),
]
