from typing import Any, List

from modules.attributes.schemas import Attributes
from modules.preferences.enums import PreferenceEnum
from pydantic import BaseModel, ConfigDict, model_validator


class PreferenceOptionRead(BaseModel):
    id: str
    name: str


class UserPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preference: PreferenceEnum
    preferred: List[PreferenceOptionRead]
    order: int | None

    @model_validator(mode="before")
    @classmethod
    def resolve_attributes(cls, data: Any) -> Any:
        if isinstance(data, dict):
            pref_type = data.get("preference")
            pref_list = data.get("preferred", [])
            order = data.get("order")
        else:
            pref_type = getattr(data, "preference", None)
            pref_list = getattr(data, "preferred", [])
            order = getattr(data, "order", None)

        enriched_preferred = []

        # Safely enrich and filter the values using the unified Attributes registry
        for val in pref_list:
            item = Attributes.get(val)
            # Ensure the option exists and belongs to the current preference category
            if item and item.preference == pref_type:
                enriched_preferred.append({"id": item.id, "name": item.name})
            elif not item:
                # Fallback for dynamic preferences (like trackers or customized keys)
                # keeping them safe and untranslated
                enriched_preferred.append({"id": val, "name": val})

        return {
            "preference": pref_type,
            "preferred": enriched_preferred,
            "order": order,
        }
