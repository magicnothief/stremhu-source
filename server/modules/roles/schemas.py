from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Role(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )

    id: str
    name: str
