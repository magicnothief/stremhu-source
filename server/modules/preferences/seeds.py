from modules.preferences.enums import PreferenceEnum
from modules.preferences.models import PreferenceModel

DEFAULT_PREFERENCES = [
    PreferenceModel(
        id=PreferenceEnum.SITE,
        name="torrent oldal",
        description="A torrent oldal, ahonnan a torrentet keressük.",
    ),
    PreferenceModel(
        id=PreferenceEnum.LANGUAGE,
        name="nyelv",
        description="A tartalom nyelve hang alapján.",
    ),
    PreferenceModel(
        id=PreferenceEnum.RESOLUTION,
        name="felbontás",
        description="A videó képmérete, felbontása.",
    ),
    PreferenceModel(
        id=PreferenceEnum.SOURCE,
        name="forrás",
        description="A kiadás forrástípusa / eredete.",
    ),
    PreferenceModel(
        id=PreferenceEnum.VIDEO_QUALITY,
        name="képminőség",
        description="A videó képi minőségi formátuma.",
    ),
    PreferenceModel(
        id=PreferenceEnum.AUDIO_QUALITY,
        name="hangminőség",
        description="A hangsáv formátuma / minősége",
    ),
    PreferenceModel(
        id=PreferenceEnum.AUDIO_SPATIAL,
        name="térhangzás",
        description="Objektumalapú surround hangzás",
    ),
]
