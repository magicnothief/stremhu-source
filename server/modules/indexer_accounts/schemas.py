import datetime

from modules.indexer_definitions.schemas import IndexerDefinition
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class IndexerAccountUpdate(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    download_full_torrent: bool | None = None
    hit_and_run: bool | None = None
    keep_seed_seconds: int | None = None


class IndexerAccountBase(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    username: str
    download_full_torrent: bool
    hit_and_run: bool | None = None
    keep_seed_seconds: int | None = None


class IndexerAccountCreate(IndexerAccountBase):
    indexer_id: str
    password: str
    cookies: dict[str, str] | None = None


class IndexerAccount(IndexerAccountBase):
    indexer_definition: IndexerDefinition
    updated_at: datetime.datetime
    created_at: datetime.datetime
