from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class UpdateSettings(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    download_limit: Optional[int] = None
    upload_limit: Optional[int] = None
    port: Optional[int] = None
    connections_limit: Optional[int] = None
    torrent_connections_limit: Optional[int] = None
    enable_upnp_and_natpmp: Optional[bool] = None


class UpdateTorrent(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    priority: Optional[int] = None


class LibTorrent(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    name: str
    info_hash: str
    download_speed: int
    upload_speed: int
    downloaded: int
    uploaded: int
    total: int
    max_connections: int
    connections: int
