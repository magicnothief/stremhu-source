from typing import Awaitable, Callable, List, Optional

from modules.attributes.models import AttributeModel
from pydantic import BaseModel


class IndexerDefinitionLogin(BaseModel):
    username: str
    password: str


class IndexerDefinitionTorrent(BaseModel):
    torrent_id: str
    download_url: str
    imdb_id: Optional[str] = None
    seeders: int = 0
    fallback_attributes: List[AttributeModel] = []


class IndexerDefinitionFindTorrentsResult(BaseModel):
    torrents: List[IndexerDefinitionTorrent] = []
    next_page: Optional[int] = None


CredentialsProvider = Optional[
    Callable[[str], Awaitable[Optional[IndexerDefinitionLogin]]]
]
