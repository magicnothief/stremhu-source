from modules.attributes.schemas import Attribute
from modules.preferences.enums import PreferenceEnum
from modules.preferences.models import UserPreferenceModel
from pydantic import BaseModel, ConfigDict


class Preference(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preference: PreferenceEnum
    preferred: list[Attribute]

    @classmethod
    def from_model(cls, model: UserPreferenceModel) -> "Preference":
        return cls(
            preference=model.definition.preference_id,
            preferred=[
                Attribute(
                    id=definition_attribute.attribute.id,
                    name=definition_attribute.attribute.name,
                )
                for definition_attribute in model.definition.definition_attributes
            ],
        )
