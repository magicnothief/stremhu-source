import asyncio
from unittest.mock import AsyncMock, Mock

from app.modules.indexer_accounts.models import IndexerAccountModel
from app.modules.indexers.service import IndexersService
from app.modules.settings.schemas.internal import SystemSettings

HIT_AND_RUN_TORRENT_IDS = ["111", "222"]
KEEP_SEED_SECONDS = 7 * 24 * 60 * 60


def create_mock_service(supports_hit_and_run: bool):
    indexer_definition = Mock()
    indexer_definition.supports_hit_and_run = supports_hit_and_run
    indexer_definition.find_hit_and_run_ids = AsyncMock(
        return_value=HIT_AND_RUN_TORRENT_IDS if supports_hit_and_run else []
    )

    indexer_definitions_service = Mock()
    indexer_definitions_service.get_by_id.return_value = indexer_definition

    torrents_service = Mock()

    service = IndexersService(
        indexer_definitions_service=indexer_definitions_service,
        indexer_accounts_service=Mock(),
        torrents_service=torrents_service,
        settings_service=Mock(),
    )

    return service, torrents_service


def run_cleanup(
    supports_hit_and_run: bool,
    keep_seed_seconds: int = 0,
):
    service, torrents_service = create_mock_service(supports_hit_and_run)

    indexer_account = IndexerAccountModel(
        indexer_id="test",
        username="test",
        password="pwd",
    )

    asyncio.run(
        service.cleanup_torrent_by_rules(
            indexer_account,
            SystemSettings(
                hit_and_run=True,
                keep_seed_seconds=keep_seed_seconds,
            ),
        )
    )

    return torrents_service.cleanup_tracker_torrents


def test_hit_and_run_list_is_used_when_supported():
    cleanup = run_cleanup(supports_hit_and_run=True)

    cleanup.assert_called_once()
    assert (
        cleanup.call_args.kwargs["not_completed_torrent_ids"] == HIT_AND_RUN_TORRENT_IDS
    )


def test_hit_and_run_list_is_skipped_when_not_supported():
    """
    Publikus trackernél (nincs Hit'n'Run) időzítő nélkül nem törlünk semmit.

    A find_for_cleanup() az üres Hit'n'Run listát "nincs megtartandó torrent"-ként
    értelmezné, és időkorlát híján minden torrentet törölne.
    """
    cleanup = run_cleanup(supports_hit_and_run=False)

    cleanup.assert_not_called()


def test_keep_seed_timer_is_used_when_hit_and_run_is_not_supported():
    cleanup = run_cleanup(
        supports_hit_and_run=False,
        keep_seed_seconds=KEEP_SEED_SECONDS,
    )

    cleanup.assert_called_once()
    assert cleanup.call_args.kwargs["keep_seed_seconds"] == KEEP_SEED_SECONDS
    assert cleanup.call_args.kwargs["not_completed_torrent_ids"] is None
