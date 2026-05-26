from typing import List

from modules.preferences.enums import PreferenceEnum
from pydantic import BaseModel, ConfigDict


class PreferenceOptionRead(BaseModel):
    id: str
    name: str


class UserPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preference: PreferenceEnum
    preferred: List[PreferenceOptionRead]
    order: int | None
