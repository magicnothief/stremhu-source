from modules.attributes.schemas import Attribute, Attributes
from modules.preferences.enums import PreferenceEnum
from pydantic import BaseModel


class Preference(BaseModel):
    id: str
    name: str
    description: str
    attributes: list[Attribute]


class Preferences(BaseModel):
    _OPTIONS = [
        Preference(
            id=PreferenceEnum.SITE,
            name="torrent oldal",
            description="A torrent oldal, ahonnan a torrentet keressük.",
            attributes=Attributes.get_by_preference(PreferenceEnum.SITE),
        ),
        Preference(
            id=PreferenceEnum.LANGUAGE,
            name="nyelv",
            description="A tartalom nyelve hang alapján.",
            attributes=Attributes.get_by_preference(PreferenceEnum.LANGUAGE),
        ),
        Preference(
            id=PreferenceEnum.RESOLUTION,
            name="felbontás",
            description="A videó képmérete, felbontása.",
            attributes=Attributes.get_by_preference(PreferenceEnum.RESOLUTION),
        ),
        Preference(
            id=PreferenceEnum.SOURCE,
            name="forrás",
            description="A kiadás forrástípusa / eredete.",
            attributes=Attributes.get_by_preference(PreferenceEnum.SOURCE),
        ),
        Preference(
            id=PreferenceEnum.VIDEO_QUALITY,
            name="képminőség",
            description="A videó képi minőségi formátuma.",
            attributes=Attributes.get_by_preference(PreferenceEnum.VIDEO_QUALITY),
        ),
        Preference(
            id=PreferenceEnum.AUDIO_QUALITY,
            name="hangminőség",
            description="A hangsáv formátuma / minősége",
            attributes=Attributes.get_by_preference(PreferenceEnum.AUDIO_QUALITY),
        ),
        Preference(
            id=PreferenceEnum.AUDIO_SPATIAL,
            name="térhangzás",
            description="Objektumalapú surround hangzás",
            attributes=Attributes.get_by_preference(PreferenceEnum.AUDIO_SPATIAL),
        ),
    ]
    _MAP = {opt.id: opt for opt in _OPTIONS}

    @classmethod
    def list(cls) -> list[Preference]:
        return cls._OPTIONS

    @classmethod
    def get(cls, id: str) -> Preference | None:
        return cls._MAP.get(id)

    @classmethod
    def is_valid(cls, id: str) -> bool:
        return id in cls._MAP
