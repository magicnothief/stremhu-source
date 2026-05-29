from common.database import get_db
from fastapi import Depends
from modules.indexer_accounts.dependencies import create_indexer_accounts_service
from modules.indexer_definitions.dependencies import get_indexer_definitions_service
from modules.indexers.service import IndexersService
from modules.torrents.dependencies import create_torrents_service
from sqlalchemy.orm import Session


def create_indexers_service(db: Session) -> IndexersService:
    indexer_accounts_service = create_indexer_accounts_service(db)
    indexer_definitions_service = get_indexer_definitions_service()
    torrents_service = create_torrents_service(db)

    return IndexersService(
        indexer_accounts_service=indexer_accounts_service,
        indexer_definitions_service=indexer_definitions_service,
        torrents_service=torrents_service,
    )


def get_indexers_service(
    db: Session = Depends(get_db),
) -> IndexersService:
    return create_indexers_service(db)
