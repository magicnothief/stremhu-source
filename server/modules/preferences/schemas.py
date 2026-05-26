from modules.attributes.models import AttributeModel
from modules.preferences.enums import PreferenceEnum
from pydantic import BaseModel


class Preference(BaseModel):
    id: PreferenceEnum
    name: str
    description: str
    attributes: list[AttributeModel]
