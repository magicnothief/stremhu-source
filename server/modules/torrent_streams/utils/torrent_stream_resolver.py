import re
from typing import Optional

import content_types
import PTN
from modules.indexers.schemas import IndexerTorrent
from modules.stremio.schemas import ParsedStreamSeries
from modules.torrent_files.models import TorrentFileModel
from modules.torrent_streams.schemas import TorrentStream
from modules.torrent_streams.utils.metadata_parser import TorrentMetadataParser
from torf import File


def is_video(filename: str) -> bool:
    content_type = content_types.get_content_type(filename)
    return bool(content_type and content_type.startswith("video/"))


def is_sample(name: str) -> bool:
    base = re.sub(r"\.[^.]+$", "", name.lower())
    return bool(re.search(r"(^sample|sample$|sample-|-sample-|-sample)", base))


def is_sample_or_trash(name: str) -> bool:
    if not is_video(name):
        return True
    return is_sample(name)


class TorrentStreamResolver:
    def __init__(
        self,
        indexer_torrent: IndexerTorrent,
        torrent_file: TorrentFileModel,
        series: Optional[ParsedStreamSeries],
    ):
        self._indexer_torrent = indexer_torrent
        self._torrent_file = torrent_file
        self._series = series

    def resolve(self) -> Optional[TorrentStream]:
        if self._series:
            torrent_file = self.resolve_series_file(self._series)
        else:
            torrent_file = self._resolve_largest_file()

        if torrent_file is None:
            return None

        # Parse torrent metadata using TorrentMetadataParser
        parse_attributes = TorrentMetadataParser(
            name=self._torrent_file.info.name or "",
            fallback_attributes=[],
        )

        parsed_attributes = parse_attributes.parse()

        return TorrentStream(
            indexer_id=self._torrent_file.indexer_id,
            torrent_id=self._torrent_file.torrent_id,
            info_hash=self._torrent_file.info_hash,
            seeders=self._indexer_torrent.seeders,
            torrent_name=self._torrent_file.info.name or "",
            attributes=parsed_attributes,
            file_name=torrent_file.name,
            file_size=torrent_file.size,
            file_index=torrent_file.index,
            play_url="",
            is_persisted_torrent=False,
        )

    def _resolve_largest_file(self) -> Optional[File]:
        valid_files = [
            file
            for file in self._torrent_file.info.files
            if is_video(str(file)) and not is_sample(str(file))
        ]
        if not valid_files:
            return None
        return max(valid_files, key=lambda file: file.size)

    def resolve_series_file(self, series: ParsedStreamSeries) -> Optional[File]:
        for file in self._torrent_file.info.files:
            normalized_name = str(file).lower()
            if is_sample_or_trash(normalized_name):
                continue

            parsed = PTN.parse(normalized_name)
            season = parsed.get("season")
            episode = parsed.get("episode")

            if season is None or episode is None:
                continue

            seasons = season if isinstance(season, list) else [season]
            episodes = episode if isinstance(episode, list) else [episode]

            if series.season in seasons and series.episode in episodes:
                return file

        return None
