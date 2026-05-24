from dataclasses import dataclass, field
from typing import Optional

from modules.attributes.enums import LanguageEnum, ResolutionEnum


@dataclass
class AdapterLoginRequest:
    """A NestJS AdapterLoginRequest portolása."""

    username: str
    password: str


@dataclass
class AdapterTorrent:
    """A NestJS AdapterTorrent portolása."""

    tracker_id: str
    torrent_id: str
    download_url: str
    imdb_id: Optional[str] = None


@dataclass
class AdapterTorrentWithInfo:
    """A NestJS AdapterTorrentWithInfo portolása – letöltési infókkal kiegészítve."""

    tracker_id: str
    torrent_id: str
    download_url: str
    language: LanguageEnum
    resolution: ResolutionEnum
    seeders: int
    imdb_id: Optional[str] = None


@dataclass
class AdapterParsedTorrent:
    """A NestJS AdapterParsedTorrent portolása – letöltött .torrent fájl bináris tartalommal."""

    torrent_id: str
    torrent_buffer: bytes


@dataclass
class FindTorrentsResult:
    """A NestJS FindTorrentsResult portolása – keresési találatok lapozással."""

    torrents: list[AdapterTorrentWithInfo] = field(default_factory=list)
    next_page: Optional[int] = None
