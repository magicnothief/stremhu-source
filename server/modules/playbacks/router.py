from fastapi import APIRouter, Depends
from modules.auth.dependencies import SessionGuard
from modules.playback_histories.dependencies import get_playback_histories_service
from modules.playback_histories.schemas.api import PlaybackHistoryResponse
from modules.playback_histories.service import PlaybackHistoriesService
from modules.playbacks.dependencies import get_playbacks_service
from modules.playbacks.schemas.api import PlaybackResponse
from modules.playbacks.service import PlaybacksService
from modules.roles.constants import UserRoleKey
from modules.users.models import UserModel

router = APIRouter(prefix="/playbacks", tags=["Playbacks"])


@router.get(
    "/",
    response_model=list[PlaybackResponse],
)
def get_list(
    playbacks_service: PlaybacksService = Depends(get_playbacks_service),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
) -> list[PlaybackResponse]:
    active_playbacks = playbacks_service.get_active_playbacks()
    return [
        PlaybackResponse.from_playback(active_playback)
        for active_playback in active_playbacks
    ]


@router.get(
    "/history",
    response_model=list[PlaybackHistoryResponse],
)
def get_history_list(
    playback_histories_service: PlaybackHistoriesService = Depends(
        get_playback_histories_service
    ),
    _: UserModel = Depends(SessionGuard([UserRoleKey.ADMIN])),
):
    playback_histories = playback_histories_service.find_list()
    return playback_histories
