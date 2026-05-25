from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AppSettings(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    instance_id: str = Field(
        default_factory=lambda: str(uuid4()),
    )
    hit_and_run: bool = True
    keep_seed_seconds: int = 0
    cache_retention_seconds: int = 14 * 24 * 60 * 60  # 14 nap másodpercekben
    catalog_token: Optional[str] = None


class UpdateAppSettings(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    instance_id: Optional[str] = None
    hit_and_run: Optional[bool] = None
    keep_seed_seconds: Optional[int] = None
    cache_retention_seconds: Optional[int] = None
    catalog_token: Optional[str] = None


class RelaySettings(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    port: int = 6881
    download_limit: int = 0
    upload_limit: int = 0
    connections_limit: int = 200
    torrent_connections_limit: int = 20
    enable_upnp_and_natpmp: bool = False


class UpdateRelaySettings(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    port: Optional[int] = None
    download_limit: Optional[int] = None
    upload_limit: Optional[int] = None
    connections_limit: Optional[int] = None
    torrent_connections_limit: Optional[int] = None
    enable_upnp_and_natpmp: Optional[bool] = None
