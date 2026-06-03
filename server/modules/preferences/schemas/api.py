from modules.attributes.schemas.api import AttributeResponse
from modules.system_preference_definitions.models import SystemPreferenceDefinitionModel
from modules.user_preference_definitions.models import UserPreferenceDefinitionModel
from pydantic import BaseModel, ConfigDict


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    attributes: list[AttributeResponse]

    @classmethod
    def from_user_preference_definition_model(
        cls,
        user_preference_definition_model: UserPreferenceDefinitionModel,
    ) -> "PreferenceResponse":
        return cls(
            id=user_preference_definition_model.definition.preference.id,
            name=user_preference_definition_model.definition.preference.name,
            description=user_preference_definition_model.definition.preference.description,
            attributes=[
                AttributeResponse(
                    id=definition_attribute.attribute.id,
                    name=definition_attribute.attribute.name,
                )
                for definition_attribute in user_preference_definition_model.definition.definition_attributes
            ],
        )

    @classmethod
    def from_system_preference_definition_model(
        cls,
        system_preference_definition_model: SystemPreferenceDefinitionModel,
    ) -> "PreferenceResponse":
        return cls(
            id=system_preference_definition_model.definition.preference.id,
            name=system_preference_definition_model.definition.preference.name,
            description=system_preference_definition_model.definition.preference.description,
            attributes=[
                AttributeResponse(
                    id=definition_attribute.attribute.id,
                    name=definition_attribute.attribute.name,
                )
                for definition_attribute in system_preference_definition_model.definition.definition_attributes
            ],
        )
