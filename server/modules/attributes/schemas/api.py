from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class AttributeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        alias_generator=to_camel,
    )

    id: str

    name: str

    short_name: str | None = None
