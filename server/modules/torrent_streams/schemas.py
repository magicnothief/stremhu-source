from typing import List

from modules.attributes.models import AttributeModel
from modules.indexers.models import IndexerModel
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class TorrentStream(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    indexer: IndexerModel
    torrent_id: str
    info_hash: str
    torrent_name: str
    file_name: str
    file_size: int
    file_index: int
    play_url: str
    seeders: int = 0
    attributes: List[AttributeModel] = []
    is_persisted_torrent: bool
