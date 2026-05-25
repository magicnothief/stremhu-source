import re
from typing import List, Optional, TypedDict

from modules.attributes.enums import (
    AudioQualityEnum,
    AudioSpatialEnum,
    LanguageEnum,
    ResolutionEnum,
    SourceEnum,
    VideoQualityEnum,
)
from modules.attributes.schemas import Attribute, Attributes
from modules.preferences.enums import PreferenceEnum


class ParsedTorrentMetadata(TypedDict):
    language: LanguageEnum
    resolution: ResolutionEnum
    video_quality: List[VideoQualityEnum]
    audio_quality: AudioQualityEnum
    audio_spatial: Optional[AudioSpatialEnum]
    source: SourceEnum


# --- RENDSZEREZETT REGEX MINTÁK ---

RESOLUTION_PATTERNS = {
    ResolutionEnum.R2160P: re.compile(
        r"(2160p|4k[-_. ](?:UHD|HEVC|BD)|(?:UHD|HEVC|BD)[-_. ]4k|\b(4k)\b|COMPLETE.UHD|UHD.COMPLETE)",
        re.IGNORECASE,
    ),
    ResolutionEnum.R1080P: re.compile(r"(1080(i|p)|1920x1080)(10bit)?", re.IGNORECASE),
    ResolutionEnum.R720P: re.compile(
        r"(720(i|p)|1280x720|960p)(10bit)?", re.IGNORECASE
    ),
    ResolutionEnum.R576P: re.compile(r"(576(i|p))", re.IGNORECASE),
    ResolutionEnum.R540P: re.compile(r"(540(i|p))", re.IGNORECASE),
    ResolutionEnum.R480P: re.compile(r"(480(i|p)|640x480|848x480)", re.IGNORECASE),
}

# --- SUBSTRING ALAPÚ MINTÁK (NestJS alapján) ---

VIDEO_QUALITY_PATTERNS = {
    VideoQualityEnum.DV: [".dolby.vision.", ".dovi.", ".dovi-", "-dovi.", ".dv."],
    VideoQualityEnum.HDR10: [
        ".hdr.",
        "-hdr.",
        ".hdr-",
        ".hdr10.",
        "-hdr10.",
        ".hdr10-",
    ],
    VideoQualityEnum.HDR10P: [
        ".hdr10plus.",
        "-hdr10plus.",
        ".hdr10plus-",
        ".hdr10+.",
        "-hdr10+.",
        ".hdr10+-",
        ".hdr10p.",
        "-hdr10p.",
        ".hdr10p-",
    ],
    VideoQualityEnum.HLG: [".hlg."],
}

AUDIO_QUALITY_PATTERNS = {
    AudioQualityEnum.TRUEHD: [".truehd."],
    AudioQualityEnum.DTS_HD_MA: [
        ".dts-hd.ma.",
        ".dtshdma.",
        ".dts-hdma.",
        ".dtsx.",
        ".dtsx.7.1.",
        ".dts.x.",
        ".dts.x7.1.",
        ".dts.x.7.1.",
    ],
    AudioQualityEnum.DD_PLUS: [
        ".ddp.",
        ".ddp5.1.",
        ".ddp7.1.",
        ".dd+.",
        ".dd+5.1.",
        ".dd+7.1.",
        ".eac3.",
    ],
    AudioQualityEnum.DTS: [".dts.", ".dts5.1."],
    AudioQualityEnum.DD: [
        ".dd.",
        ".dd2.0.",
        ".dd5.1.",
        ".dd7.1.",
        ".ac3.",
        ".ac-3.",
    ],
    AudioQualityEnum.AAC: [".aac.", ".aac2.0.", ".aac5.1."],
}

AUDIO_SPATIAL_PATTERNS = {
    AudioSpatialEnum.DTS_X: [
        ".dtsx.",
        ".dtsx.7.1.",
        ".dts.x.",
        ".dts.x7.1.",
        ".dts.x.7.1.",
    ],
    AudioSpatialEnum.DOLBY_ATMOS: [".atmos."],
}

SOURCE_PATTERNS = {
    SourceEnum.DISC_REMUX: [".remux."],
    SourceEnum.DISC_RIP: [".bluray.", ".bdrip.", ".dvdrip."],
    SourceEnum.WEB_DL: [".web-dl.", ".web_dl.", ".web-dl-rip."],
    SourceEnum.WEB_RIP: [".webrip."],
    SourceEnum.BROADCAST: [".hdtv.", ".pdtv.", ".dvb.", ".satrip."],
    SourceEnum.THEATRICAL: [".cam.", ".ts.", ".tc."],
}


class TorrentMetadataParser:
    def __init__(
        self,
        name: str,
        fallback_attributes: list[Attribute],
    ):
        self.name = name.lower()
        self.fallback_attributes = fallback_attributes

    def parse_resolution(self) -> ResolutionEnum | None:
        for res_enum, pattern in RESOLUTION_PATTERNS.items():
            if pattern.search(self.name):
                return res_enum
        for fallback_attribute in self.fallback_attributes:
            if fallback_attribute.preference == PreferenceEnum.RESOLUTION:
                return ResolutionEnum(fallback_attribute.id)
        return None

    def parse_video_quality(self) -> List[VideoQualityEnum]:
        matched = []
        for quality_enum, patterns in VIDEO_QUALITY_PATTERNS.items():
            if any(p in self.name for p in patterns):
                matched.append(quality_enum)
        return matched if matched else [VideoQualityEnum.SDR]

    def parse_audio_quality(self) -> AudioQualityEnum:
        for audio_enum, patterns in AUDIO_QUALITY_PATTERNS.items():
            if any(p in self.name for p in patterns):
                return audio_enum
        return AudioQualityEnum.UNKNOWN

    def parse_audio_spatial(self) -> Optional[AudioSpatialEnum]:
        for spatial_enum, patterns in AUDIO_SPATIAL_PATTERNS.items():
            if any(p in self.name for p in patterns):
                return spatial_enum
        return None

    def parse_source(self) -> SourceEnum:
        for source_enum, patterns in SOURCE_PATTERNS.items():
            if any(p in self.name for p in patterns):
                return source_enum
        return SourceEnum.UNKNOWN

    def parse(self) -> list[Attribute]:
        row_attribute_ids: list[str | None] = [
            self.parse_resolution(),
            *self.parse_video_quality(),
            self.parse_audio_quality(),
            *(self.parse_audio_spatial() or []),
            self.parse_source(),
        ]

        attribute_ids: list[str] = [
            row_attribute_id
            for row_attribute_id in row_attribute_ids
            if row_attribute_id is not None
        ]

        attributes: list[Attribute] = []
        for attribute_id in attribute_ids:
            attribute = Attributes.get(attribute_id)
            if attribute is None:
                continue
            attributes.append(attribute)

        return attributes
