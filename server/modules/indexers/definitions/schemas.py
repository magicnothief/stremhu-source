from typing import Awaitable, Callable, List, Optional

from modules.attributes.schemas import Attribute
from pydantic import BaseModel, Field


class IndexerDefinitionLogin(BaseModel):
    username: str
    password: str


class IndexerDefinitionTorrent(BaseModel):
    torrent_id: str
    download_url: str
    imdb_id: Optional[str] = None
    seeders: Optional[int] = None
    fallback_attributes: List[Attribute] = Field(default_factory=list)


class IndexerDefinitionFindTorrentsResult(BaseModel):
    torrents: List[IndexerDefinitionTorrent] = Field(default_factory=list)
    next_page: Optional[int] = None


CredentialsProvider = Optional[
    Callable[[str], Awaitable[Optional[IndexerDefinitionLogin]]]
]
