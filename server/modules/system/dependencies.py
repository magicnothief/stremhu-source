from common.database import get_db
from fastapi import Depends
from modules.settings.dependencies import create_settings_service
from modules.system.service import SystemService
from modules.users.dependencies import create_users_service
from sqlalchemy.orm import Session


def create_system_service(db: Session) -> SystemService:
    settings_service = create_settings_service(db)
    users_service = create_users_service(db)

    return SystemService(
        settings_service=settings_service,
        users_service=users_service,
    )


def get_system_service(
    db: Session = Depends(get_db),
) -> SystemService:
    return create_system_service(db)
