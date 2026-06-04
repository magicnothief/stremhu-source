from typing import Annotated, Literal

from modules.settings.enums import NetworkConnectionEnum, NetworkModeEnum
from pydantic import BaseModel, Field


class NetworkAutoSetup(BaseModel):
    mode: Literal[NetworkModeEnum.AUTO]
    host: str
    connection: NetworkConnectionEnum
    provider: str
    token: str
    email: str


class NetworkManualSetup(BaseModel):
    mode: Literal[NetworkModeEnum.MANUAL]
    host: str
    reverse_proxy: bool


NetworkSetup = Annotated[
    NetworkAutoSetup | NetworkManualSetup,
    Field(discriminator="mode"),
]
