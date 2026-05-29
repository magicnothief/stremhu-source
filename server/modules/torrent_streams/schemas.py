from modules.attributes.models import AttributeModel
from modules.indexer_accounts.models import IndexerAccountModel
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class TorrentStream(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    indexer_account: IndexerAccountModel
    torrent_id: str
    info_hash: str
    torrent_name: str
    file_name: str
    file_size: int
    file_index: int
    play_url: str
    seeders: int = 0
    attributes: list[AttributeModel] = []
    is_persisted_torrent: bool
