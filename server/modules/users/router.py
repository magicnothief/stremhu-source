from fastapi import APIRouter, Depends, status
from modules.auth.dependencies import SessionGuard
from modules.preferences.schemas.api import (
    PreferenceCreateRequest,
    PreferenceResponse,
    PreferencesReorderRequest,
    PreferenceUpdateRequest,
)
from modules.roles.constants import UserRoleKey
from modules.user_preference_definitions.dependencies import (
    get_user_preference_definitions_service,
)
from modules.user_preference_definitions.service import UserPreferenceDefinitionsService
from modules.users.dependencies import get_users_service
from modules.users.models import UserModel
from modules.users.schemas.api import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from modules.users.service import UsersService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_list(
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> list[UserModel]:
    return users_service.get_list()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: UserCreateRequest,
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> UserModel:
    return users_service.create(payload)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get(
    user_id: str,
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> UserModel:
    return users_service.get_by_id(user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update(
    user_id: str,
    payload: UserUpdateRequest,
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> UserModel:
    return users_service.update(user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete(
    user_id: str,
    users_service: UsersService = Depends(get_users_service),
    current_user: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> None:
    users_service.delete(user_id, current_user)


@router.put(
    "/{user_id}/api_key/regenerate",
    response_model=UserResponse,
)
def regenerate_api_key(
    user_id: str,
    users_service: UsersService = Depends(get_users_service),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> UserModel:
    return users_service.regenerate_api_key(user_id)


@router.get(
    "/{user_id}/preferences",
    response_model=list[PreferenceResponse],
)
def get_preferences(
    user_id: str,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
):
    models = user_preference_definitions_service.find_list(user_id)
    return [
        PreferenceResponse.from_user_preference_definition_model(model)
        for model in models
    ]


@router.post(
    "/{user_id}/preferences",
    response_model=PreferenceResponse,
)
def create_preference(
    user_id: str,
    payload: PreferenceCreateRequest,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> PreferenceResponse:
    model = user_preference_definitions_service.create(
        user_id,
        payload,
    )
    return PreferenceResponse.from_user_preference_definition_model(model)


@router.post(
    "/{user_id}/preferences/reorder",
    response_model=list[PreferenceResponse],
)
def reorder_preferences(
    user_id: str,
    payload: PreferencesReorderRequest,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> list[PreferenceResponse]:
    models = user_preference_definitions_service.reorder(
        user_id, payload.preference_ids
    )
    return [
        PreferenceResponse.from_user_preference_definition_model(model)
        for model in models
    ]


@router.get(
    "/{user_id}/preferences/{preference_id}",
    response_model=PreferenceResponse,
)
def get_preference(
    user_id: str,
    preference_id: str,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> PreferenceResponse:
    model = user_preference_definitions_service.get_by_id(user_id, preference_id)
    return PreferenceResponse.from_user_preference_definition_model(model)


@router.put(
    "/{user_id}/preferences/{preference_id}",
    response_model=PreferenceResponse,
)
def update_preference(
    user_id: str,
    preference_id: str,
    payload: PreferenceUpdateRequest,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> PreferenceResponse:
    model = user_preference_definitions_service.update(
        user_id,
        preference_id,
        payload,
    )
    return PreferenceResponse.from_user_preference_definition_model(model)


@router.delete(
    "/{user_id}/preferences/{preference_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_preference(
    user_id: str,
    preference_id: str,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> None:
    user_preference_definitions_service.delete(user_id, preference_id)
