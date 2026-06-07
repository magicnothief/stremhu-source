from fastapi import Depends
from modules.playback_histories.dependencies import get_playback_histories_service
from modules.playback_histories.service import PlaybackHistoriesService
from modules.playbacks.service import PlaybacksService
from modules.relay.dependencies import get_relay_service
from modules.relay.service import RelayService


def create_playbacks_service(
    relay_service: RelayService,
    playback_histories_service: PlaybackHistoriesService,
) -> PlaybacksService:
    return PlaybacksService(
        relay_service=relay_service,
        playback_histories_service=playback_histories_service,
    )


def get_playbacks_service(
    relay_service: RelayService = Depends(get_relay_service),
    playback_histories_service: PlaybackHistoriesService = Depends(
        get_playback_histories_service
    ),
) -> PlaybacksService:
    return create_playbacks_service(
        relay_service=relay_service,
        playback_histories_service=playback_histories_service,
    )
