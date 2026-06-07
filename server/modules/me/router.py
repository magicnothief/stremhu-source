from fastapi import APIRouter, Depends, HTTPException, status
from modules.auth.dependencies import OptionalSessionGuard, SessionGuard
from modules.me.schemas.api import (
    MeUpdateRequest,
)
from modules.preferences.schemas.api import (
    PreferenceCreateRequest,
    PreferenceResponse,
    PreferencesReorderRequest,
    PreferenceUpdateRequest,
)
from modules.user_preference_definitions.dependencies import (
    get_user_preference_definitions_service,
)
from modules.user_preference_definitions.service import UserPreferenceDefinitionsService
from modules.users.dependencies import get_users_service
from modules.users.models import UserModel
from modules.users.schemas.api import UserResponse
from modules.users.schemas.internal import UserUpdate
from modules.users.service import UsersService

router = APIRouter(prefix="/me", tags=["Me"])


@router.get("/", response_model=UserResponse | None)
def get(
    current_user: UserModel | None = Depends(OptionalSessionGuard()),
) -> UserModel | None:
    return current_user


@router.put("/", response_model=UserResponse)
def update(
    payload: MeUpdateRequest,
    users_service: UsersService = Depends(get_users_service),
    current_user: UserModel = Depends(SessionGuard()),
) -> UserModel:
    update_payload = payload.model_dump(exclude_unset=True)
    user_update = UserUpdate(**update_payload)

    return users_service.update(current_user.id, user_update)


@router.put("/api-key/regenerate", response_model=UserResponse)
def regenerate_api_key(
    users_service: UsersService = Depends(get_users_service),
    current_user: UserModel = Depends(SessionGuard()),
) -> UserModel:
    return users_service.regenerate_api_key(current_user.id)


@router.get(
    "/preferences",
    response_model=list[PreferenceResponse],
)
def get_preferences(
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    current_user: UserModel = Depends(SessionGuard()),
) -> list[PreferenceResponse]:
    models = user_preference_definitions_service.find_list(current_user.id)
    return [
        PreferenceResponse.from_user_preference_definition_model(model)
        for model in models
    ]


@router.post(
    "/preferences",
    response_model=PreferenceResponse,
)
def create_preference(
    payload: PreferenceCreateRequest,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    current_user: UserModel = Depends(SessionGuard()),
) -> PreferenceResponse:
    model = user_preference_definitions_service.create(
        current_user.id,
        payload,
    )
    return PreferenceResponse.from_user_preference_definition_model(model)


@router.get(
    "/preferences/{preference_id}",
    response_model=PreferenceResponse,
)
def get_preference(
    preference_id: str,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    current_user: UserModel = Depends(SessionGuard()),
) -> PreferenceResponse:
    model = user_preference_definitions_service.find_by_id(
        current_user.id, preference_id
    )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"A(z) '{preference_id}' preferencia nem található.",
        )
    return PreferenceResponse.from_user_preference_definition_model(model)


@router.post(
    "/preferences/reorder",
    response_model=list[PreferenceResponse],
)
def reorder_preferences(
    payload: PreferencesReorderRequest,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    current_user: UserModel = Depends(SessionGuard()),
) -> list[PreferenceResponse]:
    models = user_preference_definitions_service.reorder(
        current_user.id, payload.preference_ids
    )
    return [
        PreferenceResponse.from_user_preference_definition_model(model)
        for model in models
    ]


@router.put(
    "/preferences/{preference_id}",
    response_model=PreferenceResponse,
)
def update_preference(
    preference_id: str,
    payload: PreferenceUpdateRequest,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    current_user: UserModel = Depends(SessionGuard()),
) -> PreferenceResponse:
    model = user_preference_definitions_service.update(
        current_user.id,
        preference_id,
        payload,
    )
    return PreferenceResponse.from_user_preference_definition_model(model)


@router.delete(
    "/preferences/{preference_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_preference(
    preference_id: str,
    user_preference_definitions_service: UserPreferenceDefinitionsService = Depends(
        get_user_preference_definitions_service
    ),
    current_user: UserModel = Depends(SessionGuard()),
) -> None:
    user_preference_definitions_service.delete(current_user.id, preference_id)
