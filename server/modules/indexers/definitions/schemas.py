from typing import List, Optional

from modules.attributes.schemas import Attribute
from pydantic import BaseModel, Field


class IndexerDefinitionLogin(BaseModel):
    username: str
    password: str


class IndexerDefinitionTorrent(BaseModel):
    download_url: str
    imdb_id: Optional[str] = None
    seeders: Optional[int] = None
    fallback_attributes: List[Attribute] = Field([])


class IndexerDefinitionFindTorrentsResult(BaseModel):
    torrents: List[IndexerDefinitionTorrent] = Field(default_factory=list)
    next_page: Optional[int] = None
