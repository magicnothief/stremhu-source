from fastapi import APIRouter, Depends
from modules.auth.dependencies import SessionGuard
from modules.roles.enums import UserRole
from modules.settings.dependencies import get_settings_service
from modules.settings.schemas import (
    AppSettings,
    RelaySettings,
    UpdateAppSettings,
    UpdateRelaySettings,
)
from modules.settings.service import SettingsService
from modules.users.models import UserModel

router = APIRouter(
    prefix="/setting",
    tags=["Setting"],
)


@router.get(
    "/",
    response_model=AppSettings,
    operation_id="get_app_settings",
)
def get_app_settings(
    settings_service: SettingsService = Depends(get_settings_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
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
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> AppSettings:
    return settings_service.update_app_settings(payload)


@router.get(
    "/relay",
    response_model=RelaySettings,
    operation_id="get_relay_settings",
)
def get_relay_settings(
    settings_service: SettingsService = Depends(get_settings_service),
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
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
    _: UserModel = Depends(SessionGuard([UserRole.ADMIN])),
) -> RelaySettings:
    return settings_service.update_relay_settings(payload)
