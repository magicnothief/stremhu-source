import re
from typing import List, Optional

import content_types
import PTN
from modules.attributes.enums import LanguageEnum, ResolutionEnum
from modules.stremio.schemas import ParsedStreamSeries
from modules.torrent_files.schemas import TorrentFileInfo
from modules.torrent_streams.schemas import RowTorrentVideo
from modules.torrent_streams.utils.metadata_parser import TorrentMetadataParser


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


class VideoFileResolver:
    def __init__(
        self,
        tracker: str,
        torrent_id: str,
        info_hash: str,
        torrent_name: str,
        seeders: int,
        language: LanguageEnum,
        resolution: ResolutionEnum,
        files: List[TorrentFileInfo],
        series: Optional[ParsedStreamSeries] = None,
    ):
        self.tracker = tracker
        self.torrent_id = torrent_id
        self.info_hash = info_hash
        self.torrent_name = torrent_name
        self.seeders = seeders
        self.language = language
        self.resolution = resolution
        self.files = files
        self.series = series

    def resolve(self) -> Optional[RowTorrentVideo]:
        if self.series:
            torrent_file = self.resolve_series_file(self.series)
        else:
            torrent_file = self.resolve_largest_file()

        if torrent_file is None:
            return None

        # Parse torrent metadata using TorrentMetadataParser
        metadata_parser = TorrentMetadataParser(
            name=self.torrent_name,
            language_fallback=self.language,
            resolution_fallback=self.resolution,
        )
        metadata = metadata_parser.parse()

        return RowTorrentVideo(
            tracker=self.tracker,
            torrentId=self.torrent_id,
            infoHash=self.info_hash,
            seeders=self.seeders,
            torrentName=self.torrent_name,
            # Metadata
            language=metadata["language"],
            resolution=metadata["resolution"],
            video_quality=metadata["video_quality"],
            audio_quality=metadata["audio_quality"],
            audio_spatial=metadata["audio_spatial"],
            source=metadata["source"],
            # File
            fileName=torrent_file.name,
            fileSize=torrent_file.size,
            fileIndex=torrent_file.index,
            isInRelay=False,
        )

    def resolve_largest_file(self) -> Optional[TorrentFileInfo]:
        valid_files = [
            f for f in self.files if is_video(f.name) and not is_sample(f.name)
        ]
        if not valid_files:
            return None
        return max(valid_files, key=lambda f: f.size)

    def resolve_series_file(
        self, series: ParsedStreamSeries
    ) -> Optional[TorrentFileInfo]:
        for file in self.files:
            normalized_name = file.name.lower()
            if is_sample_or_trash(normalized_name):
                continue

            parsed = PTN.parse(file.name)
            season = parsed.get("season")
            episode = parsed.get("episode")

            if season is None or episode is None:
                continue

            seasons = season if isinstance(season, list) else [season]
            episodes = episode if isinstance(episode, list) else [episode]

            if series.season in seasons and series.episode in episodes:
                return file

        return None
