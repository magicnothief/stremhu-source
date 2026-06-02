from modules.preferences.constants import PreferenceKey
from modules.preferences.models import PreferenceModel

DEFAULT_PREFERENCES = [
    PreferenceModel(
        id=PreferenceKey.SITE,
        name="Torrent oldal",
        description="Az oldal, ahonnan a torrenteket keressük.",
    ),
    PreferenceModel(
        id=PreferenceKey.LANGUAGE,
        name="Nyelv",
        description="A tartalom nyelve hang alapján.",
    ),
    PreferenceModel(
        id=PreferenceKey.RESOLUTION,
        name="Felbontás",
        description="A videó képmérete, felbontása.",
    ),
    PreferenceModel(
        id=PreferenceKey.SOURCE,
        name="Forrás",
        description="A kiadás forrástípusa / eredete.",
    ),
    PreferenceModel(
        id=PreferenceKey.VIDEO_QUALITY,
        name="Képminőség",
        description="A videó képi minőségi formátuma.",
        multiple=True,
    ),
    PreferenceModel(
        id=PreferenceKey.AUDIO_QUALITY,
        name="Hangminőség",
        description="A hangsáv formátuma / minősége",
        multiple=True,
    ),
    PreferenceModel(
        id=PreferenceKey.AUDIO_SPATIAL,
        name="Térhangzás",
        description="Objektumalapú surround hangzás",
    ),
]
