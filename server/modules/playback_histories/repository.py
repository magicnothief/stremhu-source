from modules.playback_histories.models import PlaybackHistoryModel
from modules.playback_histories.schemas.internal import PlaybackHistoryCreate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload


class PlaybackHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: PlaybackHistoryCreate) -> PlaybackHistoryModel:
        playback_history = PlaybackHistoryModel(**payload.model_dump())
        self.db.add(playback_history)
        self.db.flush()
        return playback_history

    def get_or_create(self, payload: PlaybackHistoryCreate) -> PlaybackHistoryModel:
        existing = self.find_by_id(payload.playback_id)
        if existing is not None:
            return existing

        playback_history = PlaybackHistoryModel(**payload.model_dump())
        try:
            with self.db.begin_nested():
                self.db.add(playback_history)
                self.db.flush()
        except IntegrityError:
            existing = self.find_by_id(payload.playback_id)
            assert existing is not None
            return existing

        return playback_history

    def find_list(self) -> list[PlaybackHistoryModel]:
        return (
            self.db.query(PlaybackHistoryModel)
            .options(
                joinedload(PlaybackHistoryModel.user),
                joinedload(PlaybackHistoryModel.indexer_definition),
            )
            .order_by(PlaybackHistoryModel.created_at.desc())
            .all()
        )

    def find_by_id(self, playback_id: str) -> PlaybackHistoryModel | None:
        return (
            self.db.query(PlaybackHistoryModel)
            .options(
                joinedload(PlaybackHistoryModel.user),
                joinedload(PlaybackHistoryModel.indexer_definition),
            )
            .filter_by(playback_id=playback_id)
            .first()
        )

    def delete(self, playback_history: PlaybackHistoryModel) -> None:
        self.db.delete(playback_history)
        self.db.flush()
