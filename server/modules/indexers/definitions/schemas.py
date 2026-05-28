from collections.abc import Awaitable, Callable

from modules.attributes.models import AttributeModel
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class IndexerDefinition(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )

    id: str
    name: str
    url: str
    details_path: str
    requires_full_download: bool


class IndexerDefinitionLogin(BaseModel):
    username: str
    password: str


class IndexerDefinitionTorrent(BaseModel):
    torrent_id: str
    download_url: str
    imdb_id: str | None = None
    seeders: int = 0
    fallback_attributes: list[AttributeModel] = []


class IndexerDefinitionFindTorrentsResult(BaseModel):
    torrents: list[IndexerDefinitionTorrent] = []
    next_page: int | None = None


CredentialsProvider = Callable[[str], Awaitable[IndexerDefinitionLogin | None]] | None
