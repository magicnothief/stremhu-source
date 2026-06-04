import asyncio
import os
import sys

from common.logger import logger
from config import config
from modules.settings.service import SettingsService
from modules.system.schemas.internal import SystemStatus
from modules.users.service import UsersService


class SystemService:
    def __init__(
        self,
        users_service: UsersService,
        settings_service: SettingsService,
    ):
        self._users_service = users_service
        self._settings_service = settings_service

    def status(self) -> SystemStatus:
        has_user = self._users_service.count() > 0
        app_url = self._settings_service.get_app_url()

        return SystemStatus(
            configured=has_user,
            app_url=app_url,
            version=config.version,
        )

    async def restart(self):
        await asyncio.sleep(2)
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            logger.critical(
                "Súlyos hiba történt az automatikus újraindítás során: %s", e
            )
