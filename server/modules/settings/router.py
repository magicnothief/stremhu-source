from common.enums import UserRole
from fastapi import APIRouter, Depends
from modules.auth.roles import RoleChecker
from modules.settings.dependencies import get_settings_service
from modules.settings.schemas import (
    AppSettings,
    RelaySettings,
    UpdateAppSettings,
    UpdateRelaySettings,
)
from modules.settings.service import SettingsService
from modules.users.models import UserModel
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

router = APIRouter(
    prefix="/setting",
    tags=["Setting"],
)


class LocalUrlRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
    ipv4: str


class LocalUrlResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
    local_url: str


@router.get(
    "/",
    response_model=AppSettings,
    operation_id="get_app_settings",
)
def get_app_settings(
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: UserModel = Depends(RoleChecker([UserRole.ADMIN])),
) -> AppSettings:
    return settings_service.get_app_settings()


@router.put(
    "/",
    response_model=AppSettings,
    operation_id="update_app_settings",
)
def update_app_settings(
    payload: UpdateAppSettings,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: UserModel = Depends(RoleChecker([UserRole.ADMIN])),
) -> AppSettings:
    return settings_service.update_app_settings(payload)


@router.get(
    "/relay",
    response_model=RelaySettings,
    operation_id="get_relay_settings",
)
def get_relay_settings(
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: UserModel = Depends(RoleChecker([UserRole.ADMIN])),
) -> RelaySettings:
    return settings_service.get_relay_settings()


@router.put(
    "/relay",
    response_model=RelaySettings,
    operation_id="update_relay_settings",
)
def update_relay_settings(
    payload: UpdateRelaySettings,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: UserModel = Depends(RoleChecker([UserRole.ADMIN])),
) -> RelaySettings:
    return settings_service.update_relay_settings(payload)
