import datetime
import uuid

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PairingBaseSchema(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        alias_generator=to_camel,
    )


class PairInit(PairingBaseSchema):
    user_code: str
    device_code: uuid.UUID
    expires_at: datetime.datetime


class PairStatusRequest(PairingBaseSchema):
    device_code: uuid.UUID


class PairStatus(PairingBaseSchema):
    status: str
    token: uuid.UUID | None = None


class PairVerifyRequest(PairingBaseSchema):
    user_code: str


class PairVerify(PairingBaseSchema):
    success: bool
