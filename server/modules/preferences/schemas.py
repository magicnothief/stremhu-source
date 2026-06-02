from modules.attributes.schemas import Attribute
from modules.user_preference_definitions.models import UserPreferenceDefinitionModel
from pydantic import BaseModel, ConfigDict


class Preference(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    attributes: list[Attribute]

    @classmethod
    def from_model(cls, model: UserPreferenceDefinitionModel) -> "Preference":
        return cls(
            id=model.definition.preference.id,
            name=model.definition.preference.name,
            description=model.definition.preference.description,
            attributes=[
                Attribute(
                    id=definition_attribute.attribute.id,
                    name=definition_attribute.attribute.name,
                )
                for definition_attribute in model.definition.definition_attributes
            ],
        )
