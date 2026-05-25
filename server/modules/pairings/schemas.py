import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PairingBaseSchema(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class PairInit(PairingBaseSchema):
    user_code: str
    device_code: str
    expires_at: datetime.datetime


class PairStatusRequest(PairingBaseSchema):
    device_code: str


class PairStatus(PairingBaseSchema):
    status: str
    token: str | None = None


class PairVerifyRequest(PairingBaseSchema):
    user_code: str


class PairVerify(PairingBaseSchema):
    success: bool
