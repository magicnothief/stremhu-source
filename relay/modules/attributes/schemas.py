from typing import Dict, List, Optional

from modules.attributes.enums import (
    AudioQualityEnum,
    AudioSpatialEnum,
    LanguageEnum,
    ResolutionEnum,
    SourceEnum,
    VideoQualityEnum,
)
from modules.preferences.enums import PreferenceEnum
from pydantic import BaseModel


class Attribute(BaseModel):
    id: str
    name: str
    preference: PreferenceEnum | None = None


class Attributes(BaseModel):
    _OPTIONS = [
        # Resolutions
        Attribute(
            id=ResolutionEnum.R2160P,
            name="UHD (4K)",
            preference=PreferenceEnum.RESOLUTION,
        ),
        Attribute(
            id=ResolutionEnum.R1080P,
            name="Full HD (1080p)",
            preference=PreferenceEnum.RESOLUTION,
        ),
        Attribute(
            id=ResolutionEnum.R720P,
            name="HD (720p)",
            preference=PreferenceEnum.RESOLUTION,
        ),
        Attribute(
            id=ResolutionEnum.R576P,
            name="SD (576p)",
            preference=PreferenceEnum.RESOLUTION,
        ),
        Attribute(
            id=ResolutionEnum.R540P,
            name="SD (540p)",
            preference=PreferenceEnum.RESOLUTION,
        ),
        Attribute(
            id=ResolutionEnum.R480P,
            name="SD (480p)",
            preference=PreferenceEnum.RESOLUTION,
        ),
        # Languages
        Attribute(
            id=LanguageEnum.HU,
            name="magyar",
            preference=PreferenceEnum.LANGUAGE,
        ),
        Attribute(
            id=LanguageEnum.EN,
            name="angol",
            preference=PreferenceEnum.LANGUAGE,
        ),
        # Video Qualities
        Attribute(
            id=VideoQualityEnum.DV,
            name="Dolby Vision",
            preference=PreferenceEnum.VIDEO_QUALITY,
        ),
        Attribute(
            id=VideoQualityEnum.HDR10P,
            name="HDR10+",
            preference=PreferenceEnum.VIDEO_QUALITY,
        ),
        Attribute(
            id=VideoQualityEnum.HDR10,
            name="HDR10",
            preference=PreferenceEnum.VIDEO_QUALITY,
        ),
        Attribute(
            id=VideoQualityEnum.HLG,
            name="HLG",
            preference=PreferenceEnum.VIDEO_QUALITY,
        ),
        Attribute(
            id=VideoQualityEnum.SDR,
            name="SDR",
            preference=PreferenceEnum.VIDEO_QUALITY,
        ),
        # Sources
        Attribute(
            id=SourceEnum.DISC_REMUX,
            name="Lemez (Remux - eredeti minőség)",
            preference=PreferenceEnum.SOURCE,
        ),
        Attribute(
            id=SourceEnum.DISC_RIP,
            name="Lemez (Rip / újrakódolt)",
            preference=PreferenceEnum.SOURCE,
        ),
        Attribute(
            id=SourceEnum.WEB_DL,
            name="Streaming (WEB-DL - eredeti)",
            preference=PreferenceEnum.SOURCE,
        ),
        Attribute(
            id=SourceEnum.WEB_RIP,
            name="Streaming (WEBRip - újrakódolt)",
            preference=PreferenceEnum.SOURCE,
        ),
        Attribute(
            id=SourceEnum.BROADCAST,
            name="TV (HDTV / közvetített)",
            preference=PreferenceEnum.SOURCE,
        ),
        Attribute(
            id=SourceEnum.THEATRICAL,
            name="Mozis felvétel (CAM/TS/TC)",
            preference=PreferenceEnum.SOURCE,
        ),
        Attribute(
            id=SourceEnum.UNKNOWN,
            name="Egyéb",
            preference=PreferenceEnum.SOURCE,
        ),
        # Audio Qualities
        Attribute(
            id=AudioQualityEnum.TRUEHD,
            name="Dolby TrueHD",
            preference=PreferenceEnum.AUDIO_QUALITY,
        ),
        Attribute(
            id=AudioQualityEnum.DTS_HD_MA,
            name="DTS-HD Master Audio",
            preference=PreferenceEnum.AUDIO_QUALITY,
        ),
        Attribute(
            id=AudioQualityEnum.DD_PLUS,
            name="Dolby Digital Plus",
            preference=PreferenceEnum.AUDIO_QUALITY,
        ),
        Attribute(
            id=AudioQualityEnum.DTS,
            name="DTS Core",
            preference=PreferenceEnum.AUDIO_QUALITY,
        ),
        Attribute(
            id=AudioQualityEnum.DD,
            name="Dolby Digital",
            preference=PreferenceEnum.AUDIO_QUALITY,
        ),
        Attribute(
            id=AudioQualityEnum.AAC,
            name="AAC",
            preference=PreferenceEnum.AUDIO_QUALITY,
        ),
        Attribute(
            id=AudioQualityEnum.UNKNOWN,
            name="Egyéb",
            preference=PreferenceEnum.AUDIO_QUALITY,
        ),
        # Audio Spatials
        Attribute(
            id=AudioSpatialEnum.DTS_X,
            name="DTS:X",
            preference=PreferenceEnum.AUDIO_SPATIAL,
        ),
        Attribute(
            id=AudioSpatialEnum.DOLBY_ATMOS,
            name="Dolby Atmos",
            preference=PreferenceEnum.AUDIO_SPATIAL,
        ),
    ]

    _MAP: Dict[str, Attribute] = {opt.id: opt for opt in _OPTIONS}

    @classmethod
    def list(cls) -> List[Attribute]:
        """Visszaadja az összes elérhető opciót."""
        return cls._OPTIONS

    @classmethod
    def get_by_preference(cls, preference: PreferenceEnum) -> List[Attribute]:
        """Visszaadja az összes elérhető opciót az adott preferencia szerint."""
        return [opt for opt in cls._OPTIONS if opt.preference == preference]

    @classmethod
    def get(cls, id: str) -> Optional[Attribute]:
        """Lekér egy konkrét elemet az ID alapján."""
        return cls._MAP.get(id)

    @classmethod
    def is_valid(cls, id: str) -> bool:
        """Ellenőrzi, hogy a megadott ID létezik-e az opciók között."""
        return id in cls._MAP
