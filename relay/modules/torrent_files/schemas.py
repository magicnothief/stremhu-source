from typing import List, Self

from modules.torrent_files.exceptions import InvalidTorrentFileException
from pydantic import BaseModel, Field, PrivateAttr, computed_field, model_validator
from torf import Torrent


class TorrentFileInfo(BaseModel):
    name: str
    index: int
    size: int


class TorrentInfo(BaseModel):
    info_hash: str
    name: str
    size: int
    files: List[TorrentFileInfo]


class TorrentFile(BaseModel):
    indexer_id: str
    torrent_id: str
    torrent_bytes: bytes = Field(repr=False)

    _info: TorrentInfo | None = PrivateAttr(default=None)

    @model_validator(mode="after")
    def validate_and_extract_info(self) -> Self:
        try:
            torrent = Torrent.read_stream(self.torrent_bytes)
            torrent.validate()

            files = [
                TorrentFileInfo(name=str(file), index=index, size=file.size)
                for index, file in enumerate(torrent.files)
            ]

            self._info = TorrentInfo(
                info_hash=torrent.infohash,
                name=torrent.name or "",
                size=torrent.size,
                files=files,
            )

            return self

        except Exception:
            raise InvalidTorrentFileException()

    @computed_field
    @property
    def info(self) -> TorrentInfo:
        assert self._info is not None, "A torrent info nem érhető el!"
        return self._info


class TorrentFilesFilter(BaseModel):
    indexer_id: str | None = None
    torrent_id: str | None = None
