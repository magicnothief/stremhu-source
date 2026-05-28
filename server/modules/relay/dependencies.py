from functools import lru_cache

from modules.relay.service import RelayService


@lru_cache
def get_relay_service() -> RelayService:
    return RelayService()
