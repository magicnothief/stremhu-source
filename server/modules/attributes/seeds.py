from modules.attributes.constants import AttributeKey
from modules.attributes.models import AttributeModel
from modules.preferences.constants import PreferenceKey

DEFAULT_ATTRIBUTES = [
    # Resolutions
    AttributeModel(
        id=AttributeKey.R2160P,
        name="UHD (4K)",
        preference_id=PreferenceKey.RESOLUTION,
        pattern=r"(2160p|4k[-_. ](?:UHD|HEVC|BD)|(?:UHD|HEVC|BD)[-_. ]4k|\b(4k)\b|COMPLETE.UHD|UHD.COMPLETE)",
    ),
    AttributeModel(
        id=AttributeKey.R1080P,
        name="Full HD (1080p)",
        preference_id=PreferenceKey.RESOLUTION,
        pattern=r"(1080(i|p)|1920x1080)(10bit)?",
    ),
    AttributeModel(
        id=AttributeKey.R720P,
        name="HD (720p)",
        preference_id=PreferenceKey.RESOLUTION,
        pattern=r"(720(i|p)|1280x720|960p)(10bit)?",
    ),
    AttributeModel(
        id=AttributeKey.R576P,
        name="SD (576p)",
        preference_id=PreferenceKey.RESOLUTION,
        pattern=r"(576(i|p))",
    ),
    AttributeModel(
        id=AttributeKey.R540P,
        name="SD (540p)",
        preference_id=PreferenceKey.RESOLUTION,
        pattern=r"(540(i|p))",
    ),
    AttributeModel(
        id=AttributeKey.R480P,
        name="SD (480p)",
        preference_id=PreferenceKey.RESOLUTION,
        pattern=r"(480(i|p)|640x480|848x480)",
    ),
    # Languages
    AttributeModel(
        id=AttributeKey.HUN,
        name="magyar",
        preference_id=PreferenceKey.LANGUAGE,
        pattern=r"\b(hun(?:[-_. ]?dub)?|magyar|hungarian)\b",
    ),
    AttributeModel(
        id=AttributeKey.ENG,
        name="angol",
        preference_id=PreferenceKey.LANGUAGE,
        pattern=r"\b(eng(?:[-_. ]?dub)?|english)\b",
    ),
    # Video Qualities
    AttributeModel(
        id=AttributeKey.DV,
        name="Dolby Vision",
        preference_id=PreferenceKey.VIDEO_QUALITY,
        pattern=r"\b(dolby[-_. ]?vision|dovi|dv)\b",
    ),
    AttributeModel(
        id=AttributeKey.HDR10P,
        name="HDR10+",
        preference_id=PreferenceKey.VIDEO_QUALITY,
        pattern=r"\b(hdr10(?:plus|p|\+))\b",
    ),
    AttributeModel(
        id=AttributeKey.HDR10,
        name="HDR10",
        preference_id=PreferenceKey.VIDEO_QUALITY,
        pattern=r"\b(hdr10)\b",
    ),
    AttributeModel(
        id=AttributeKey.HLG,
        name="HLG",
        preference_id=PreferenceKey.VIDEO_QUALITY,
        pattern=r"\b(hlg)\b",
    ),
    AttributeModel(
        id=AttributeKey.SDR,
        name="SDR",
        preference_id=PreferenceKey.VIDEO_QUALITY,
        pattern=None,
    ),
    # Sources
    AttributeModel(
        id=AttributeKey.DISC_REMUX,
        name="Lemez (Remux - eredeti minőség)",
        preference_id=PreferenceKey.SOURCE,
        pattern=r"\b(remux)\b",
    ),
    AttributeModel(
        id=AttributeKey.DISC_RIP,
        name="Lemez (Rip / újrakódolt)",
        preference_id=PreferenceKey.SOURCE,
        pattern=r"\b(bluray|bdrip|dvdrip)\b",
    ),
    AttributeModel(
        id=AttributeKey.WEB_DL,
        name="Streaming (WEB-DL - eredeti)",
        preference_id=PreferenceKey.SOURCE,
        pattern=r"\b(web[-_. ]?dl(?:[-_. ]?rip)?)\b",
    ),
    AttributeModel(
        id=AttributeKey.WEB_RIP,
        name="Streaming (WEBRip - újrakódolt)",
        preference_id=PreferenceKey.SOURCE,
        pattern=r"\b(webrip)\b",
    ),
    AttributeModel(
        id=AttributeKey.BROADCAST,
        name="TV (HDTV / közvetített)",
        preference_id=PreferenceKey.SOURCE,
        pattern=r"\b(hdtv|pdtv|dvb|satrip)\b",
    ),
    AttributeModel(
        id=AttributeKey.THEATRICAL,
        name="Mozis felvétel (CAM/TS/TC)",
        preference_id=PreferenceKey.SOURCE,
        pattern=r"\b(cam|ts|tc)\b",
    ),
    # Audio Qualities
    AttributeModel(
        id=AttributeKey.TRUEHD,
        name="Dolby TrueHD",
        preference_id=PreferenceKey.AUDIO_QUALITY,
        pattern=r"\b(truehd)\b",
    ),
    AttributeModel(
        id=AttributeKey.DTS_HD_MA,
        name="DTS-HD Master Audio",
        preference_id=PreferenceKey.AUDIO_QUALITY,
        pattern=r"\b(dts[-_. ]?hd[-_. ]?ma|dtshdma|dts[-_. ]?x(?:[-_. ]?7\.1)?)\b",
    ),
    AttributeModel(
        id=AttributeKey.DD_PLUS,
        name="Dolby Digital Plus",
        preference_id=PreferenceKey.AUDIO_QUALITY,
        pattern=r"\b(ddp(?:5\.1|7\.1)?|dd\+(?:5\.1|7\.1)?|eac3)\b",
    ),
    AttributeModel(
        id=AttributeKey.DTS,
        name="DTS Core",
        preference_id=PreferenceKey.AUDIO_QUALITY,
        pattern=r"\b(dts(?:5\.1)?)\b",
    ),
    AttributeModel(
        id=AttributeKey.DD,
        name="Dolby Digital",
        preference_id=PreferenceKey.AUDIO_QUALITY,
        pattern=r"\b(dd(?:2\.0|5\.1|7\.1)?|ac[-_. ]?3)\b",
    ),
    AttributeModel(
        id=AttributeKey.AAC,
        name="AAC",
        preference_id=PreferenceKey.AUDIO_QUALITY,
        pattern=r"\b(aac(?:2\.0|5\.1)?)\b",
    ),
    # Audio Spatials
    AttributeModel(
        id=AttributeKey.DTS_X,
        name="DTS:X",
        preference_id=PreferenceKey.AUDIO_SPATIAL,
        pattern=r"\b(dts[-_. ]?x(?:[-_. ]?7\.1)?)\b",
    ),
    AttributeModel(
        id=AttributeKey.DOLBY_ATMOS,
        name="Dolby Atmos",
        preference_id=PreferenceKey.AUDIO_SPATIAL,
        pattern=r"\b(atmos)\b",
    ),
    # Others
    AttributeModel(
        id=AttributeKey.THREE_D,
        name="3D",
        preference_id=None,
        pattern=r"\b(3d|hsbs|hou|half[-_. ]?(?:sbs|ou))\b",
    ),
]
