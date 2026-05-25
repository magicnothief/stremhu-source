from enum import Enum


class LanguageEnum(str, Enum):
    HU = "hu"
    EN = "en"


class ResolutionEnum(str, Enum):
    R2160P = "2160p"
    R1080P = "1080p"
    R720P = "720p"
    R576P = "576p"
    R540P = "540p"
    R480P = "480p"


class VideoQualityEnum(str, Enum):
    DV = "dolby-vision"
    HDR10P = "hdr10+"
    HDR10 = "hdr10"
    HLG = "hlg"
    SDR = "sdr"


class SourceEnum(str, Enum):
    DISC_REMUX = "disc-remux"
    DISC_RIP = "disc-rip"
    WEB_DL = "web-dl"
    WEB_RIP = "web-rip"
    BROADCAST = "broadcast"
    THEATRICAL = "theatrical"
    UNKNOWN = "unknown"


class AudioQualityEnum(str, Enum):
    TRUEHD = "truehd"
    DTS_HD_MA = "dts-hd-ma"
    DD_PLUS = "ddp"
    DTS = "dts"
    DD = "dd"
    AAC = "aac"
    UNKNOWN = "unknown"


class AudioSpatialEnum(str, Enum):
    DOLBY_ATMOS = "dolby-atmos"
    DTS_X = "dts-x"
