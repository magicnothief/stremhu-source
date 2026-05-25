from common.database import get_db
from fastapi import Depends
from modules.pairings.repository import PairingsRepository
from modules.pairings.service import PairingsService
from sqlalchemy.orm import Session


def _get_pairings_repository(db: Session = Depends(get_db)) -> PairingsRepository:
    return PairingsRepository(db)


def get_pairings_service(
    pairings_repository: PairingsRepository = Depends(_get_pairings_repository),
) -> PairingsService:
    return PairingsService(pairings_repository)
