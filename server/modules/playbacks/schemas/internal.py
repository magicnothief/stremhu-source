from dataclasses import dataclass
from typing import TYPE_CHECKING

from modules.playback_histories.models import PlaybackHistoryModel

if TYPE_CHECKING:
    from modules.relay.entities import Stream


@dataclass
class Playback:
    playback_history_model: PlaybackHistoryModel
    stream: "Stream"
