import asyncio
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from fastapi import HTTPException, status
from modules.attributes.enums import (
    AudioQualityEnum,
    AudioSpatialEnum,
    LanguageEnum,
    ResolutionEnum,
    SourceEnum,
    VideoQualityEnum,
)
from modules.attributes.schemas import Attribute, Attributes
from modules.indexers.definitions.service import IndexerDefinitionsService
from modules.indexers.service import IndexersService
from modules.persisted_torrents.service import TorrentsService
from modules.stremio.schemas import ParsedStreamSeries
from modules.torrent_files.service import TorrentFilesService
from modules.torrent_streams.schemas import (
    RowTorrentVideo,
    TorrentStream,
    TorrentVideo,
    TrackerOption,
)
from modules.torrent_streams.utils.metadata_parser import TorrentMetadataParser
from modules.torrent_streams.utils.video_resolver import VideoFileResolver, is_sample_or_trash
from modules.users.models import UserModel

logger = logging.getLogger(__name__)


class TorrentStreamsService:
    def __init__(
        self,
        db: Session,
        indexers_service: IndexersService,
        indexer_definitions_service: IndexerDefinitionsService,
        torrent_files_service: TorrentFilesService,
        torrents_service: TorrentsService,
    ):
        self.db = db
        self.indexers_service = indexers_service
        self.indexer_definitions_service = indexer_definitions_service
        self.torrent_files_service = torrent_files_service
        self.torrents_service = torrents_service

    async def find_by_imdb(
        self,
        user: UserModel,
        imdb_id: str,
        series: Optional[ParsedStreamSeries] = None,
        media_type: Optional[str] = None,
    ) -> Tuple[List[TorrentVideo], List[str]]:
        # 1. Lekérjük az összes bejelentkezett indexert
        indexers = self.indexers_service.get_list()
        if not indexers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Használat előtt konfigurálnod kell legalább egy tracker bejelentkezést.",
            )

        # 2. Torrentek párhuzamos keresése az összes indexeren
        search_tasks = []
        for indexer in indexers:
            try:
                definition = self.indexer_definitions_service.find_one_by_id(indexer.id)
                search_tasks.append((indexer.id, definition.find(imdb_id)))
            except Exception as e:
                logger.error(
                    f"Hiba az indexer definíció feloldásakor: {indexer.id}", exc_info=e
                )

        tracker_errors = []
        all_tracker_torrents = []

        if search_tasks:
            indexer_ids, tasks = zip(*search_tasks)
            search_results = await asyncio.gather(*tasks, return_exceptions=True)

            for indexer_id, result in zip(indexer_ids, search_results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Hiba történt a(z) {indexer_id} keresése közben: {result}"
                    )
                    tracker_errors.append(str(result))
                else:
                    all_tracker_torrents.extend(result)

        # 3. Cache-elt fájlok lekérése és fájlok feloldása
        # Párhuzamosan ellenőrizzük és töltjük le a .torrent fájlokat
        resolve_tasks = []
        for torrent in all_tracker_torrents:
            resolve_tasks.append(self._resolve_torrent_files(torrent))

        resolved_torrents = await asyncio.gather(*resolve_tasks, return_exceptions=True)

        row_videos: List[RowTorrentVideo] = []
        for torrent_data, result in zip(all_tracker_torrents, resolved_torrents):
            if isinstance(result, Exception):
                logger.error(
                    f"Nem sikerült a torrent fájlt feloldani a(z) {torrent_data.tracker_id} - {torrent_data.torrent_id} esetén.",
                    exc_info=result,
                )
                tracker_errors.append(str(result))
                continue

            if not result:
                continue

            # Fájl feloldása film vagy sorozat alapján
            resolver = VideoFileResolver(
                tracker=torrent_data.tracker_id,
                torrent_id=torrent_data.torrent_id,
                info_hash=result.info_hash,
                torrent_name=result.info.name,
                seeders=torrent_data.seeders,
                language=torrent_data.language,
                resolution=torrent_data.resolution,
                files=result.info.files,
                series=series,
            )
            resolved_video = resolver.resolve()
            if resolved_video:
                row_videos.append(resolved_video)

        # 4. Szűrés felhasználói beállítások alapján
        filtered_videos = self.filter_torrent_videos(row_videos, user)

        # 5. Sorbarendezés
        sorted_videos = self.sort_torrent_videos(filtered_videos)

        # 6. DTO Mapping a válasz formátumra
        mapped_videos = []
        # TODO: Ha elkészül a globális beállítások modul, onnan kell az endpoint-ot lekérdezni
        endpoint = "http://localhost:4300"

        for video in sorted_videos:
            # Indexer név feloldása a válaszhoz
            try:
                definition = self.indexer_definitions_service.find_one_by_id(
                    video.tracker
                )
                tracker_name = definition.name
            except Exception:
                tracker_name = video.tracker

            attributes = self._build_attributes_from_row(video)

            mapped_videos.append(
                TorrentVideo(
                    tracker=TrackerOption(id=video.tracker, name=tracker_name),
                    torrentId=video.torrent_id,
                    infoHash=video.info_hash,
                    torrentName=video.torrent_name,
                    fileName=video.file_name,
                    fileSize=self._format_filesize(video.file_size),
                    fileIndex=video.file_index,
                    playUrl=f"{endpoint}/api/{user.token}/play/{video.tracker}/{video.torrent_id}/{video.file_index}",
                    seeders=video.seeders,
                    isInRelay=video.is_in_relay,
                    attributes=attributes,
                )
            )

        return mapped_videos, tracker_errors

    async def find_by_torrent_id(
        self,
        user: UserModel,
        tracker: str,
        torrent_id: str,
    ) -> List[TorrentStream]:
        # Töltse le és tegye a cache-be, ha még nincs meg
        torrent_cache = await self._resolve_torrent_by_id(tracker, torrent_id)
        if not torrent_cache:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Torrent nem található.",
            )

        try:
            definition = self.indexer_definitions_service.find_one_by_id(tracker)
            tracker_name = definition.name
        except Exception:
            tracker_name = tracker

        endpoint = "http://localhost:4300"
        streams = []

        # Torrent nevének parsolásával előállítjuk az attribútum tömböt
        metadata_parser = TorrentMetadataParser(
            name=torrent_cache.info.name,
            language_fallback=LanguageEnum.HU,
            resolution_fallback=ResolutionEnum.R1080P,
        )
        metadata = metadata_parser.parse()
        attributes = self._build_attributes(metadata)

        for file in torrent_cache.info.files:
            # Minták és szemét fájlok szűrése
            if is_sample_or_trash(file.name):
                continue

            streams.append(
                TorrentStream(
                    tracker=TrackerOption(id=tracker, name=tracker_name),
                    torrentId=torrent_id,
                    infoHash=torrent_cache.info_hash,
                    torrentName=torrent_cache.info.name,
                    fileName=file.name,
                    fileSize=self._format_filesize(file.size),
                    fileIndex=file.index,
                    playUrl=f"{endpoint}/api/{user.token}/play/{tracker}/{torrent_id}/{file.index}",
                    attributes=attributes,
                )
            )

        # Sorbarendezzük név szerint
        streams.sort(key=lambda s: s.file_name)
        return streams

    def filter_torrent_videos(
        self,
        torrent_videos: List[RowTorrentVideo],
        user: UserModel,
    ) -> List[RowTorrentVideo]:
        filtered = []
        for video in torrent_videos:
            # Seed szűrés, ha a felhasználónál be van állítva minimum limit
            if user.torrent_seed is not None and video.seeders <= user.torrent_seed:
                continue

            # (Idővel ide kerülnek a felhasználói tiltólistás szűrések is)
            filtered.append(video)

        return filtered

    def sort_torrent_videos(
        self,
        torrent_videos: List[RowTorrentVideo],
    ) -> List[RowTorrentVideo]:
        # Lekérjük az aktív libtorrent letöltések info_hash listáját, hogy lássuk mi van már a relay-ben
        active_torrents = self.torrents_service.get_torrents()
        active_hashes = {t.info_hash.lower() for t in active_torrents}

        for video in torrent_videos:
            video.is_in_relay = video.info_hash.lower() in active_hashes

        # Rendezés:
        # 1. isInRelay (True előre: False -> 1, True -> 0, így asc szerint a True lesz elöl)
        # 2. Seeders szerint csökkenő sorrendben (desc)
        torrent_videos.sort(
            key=lambda v: (
                0 if v.is_in_relay else 1,
                -v.seeders,
            )
        )

        return torrent_videos

    def _build_attributes(self, metadata) -> List[Attribute]:
        attributes = []

        # Nyelv
        if metadata.get("language"):
            lang = Attributes.get(metadata["language"])
            if lang:
                attributes.append(lang)

        # Felbontás
        if metadata.get("resolution"):
            res = Attributes.get(metadata["resolution"])
            if res:
                attributes.append(res)

        # Képminőségek
        for vq in metadata.get("video_quality", []):
            if vq != VideoQualityEnum.SDR:
                vq_attr = Attributes.get(vq)
                if vq_attr:
                    attributes.append(vq_attr)

        # Hangminőség
        if (
            metadata.get("audio_quality")
            and metadata["audio_quality"] != AudioQualityEnum.UNKNOWN
        ):
            aq = Attributes.get(metadata["audio_quality"])
            if aq:
                attributes.append(aq)

        # Térhangzás
        if metadata.get("audio_spatial"):
            asp = Attributes.get(metadata["audio_spatial"])
            if asp:
                attributes.append(asp)

        # Forrás
        if metadata.get("source"):
            src = Attributes.get(metadata["source"])
            if src:
                attributes.append(src)

        return attributes

    def _build_attributes_from_row(self, video: RowTorrentVideo) -> List[Attribute]:
        attributes = []

        # Nyelv
        if video.language:
            lang = Attributes.get(video.language)
            if lang:
                attributes.append(lang)

        # Felbontás
        if video.resolution:
            res = Attributes.get(video.resolution)
            if res:
                attributes.append(res)

        # Képminőségek
        for vq in video.video_quality:
            if vq != VideoQualityEnum.SDR:
                vq_attr = Attributes.get(vq)
                if vq_attr:
                    attributes.append(vq_attr)

        # Hangminőség
        if video.audio_quality and video.audio_quality != AudioQualityEnum.UNKNOWN:
            aq = Attributes.get(video.audio_quality)
            if aq:
                attributes.append(aq)

        # Térhangzás
        if video.audio_spatial:
            asp = Attributes.get(video.audio_spatial)
            if asp:
                attributes.append(asp)

        # Forrás
        if video.source:
            src = Attributes.get(video.source)
            if src:
                attributes.append(src)

        return attributes

    async def _resolve_torrent_files(self, torrent_data) -> Optional[any]:
        # Megnézzük a cache-ben
        cached = self.torrent_files_service.get_one(
            indexer_id=torrent_data.tracker_id,
            torrent_id=torrent_data.torrent_id,
        )
        if cached:
            return cached

        # Ha nincs meg, letöltjük
        definition = self.indexer_definitions_service.find_one_by_id(
            torrent_data.tracker_id
        )
        adapter_torrent = await definition.find_one(torrent_data.torrent_id)
        downloaded = await definition.download(adapter_torrent)

        # Hozzáadjuk a cache-hez
        return self.torrent_files_service.create(
            indexer_id=torrent_data.tracker_id,
            torrent_id=torrent_data.torrent_id,
            torrent_bytes=downloaded.torrent_buffer,
        )

    async def _resolve_torrent_by_id(
        self, tracker: str, torrent_id: str
    ) -> Optional[any]:
        cached = self.torrent_files_service.get_one(
            indexer_id=tracker,
            torrent_id=torrent_id,
        )
        if cached:
            return cached

        definition = self.indexer_definitions_service.find_one_by_id(tracker)
        adapter_torrent = await definition.find_one(torrent_id)
        downloaded = await definition.download(adapter_torrent)

        return self.torrent_files_service.create(
            indexer_id=tracker,
            torrent_id=torrent_id,
            torrent_bytes=downloaded.torrent_buffer,
        )

    def _format_filesize(self, bytes_size: int) -> str:
        """Méret formázása olvasható szöveggé."""
        if bytes_size == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        import math

        i = int(math.floor(math.log(bytes_size, 1024)))
        p = math.pow(1024, i)
        s = round(bytes_size / p, 2)
        return f"{s} {size_name[i]}"
