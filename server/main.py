import asyncio
import json
from contextlib import asynccontextmanager

import pydash
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import NodeEnv, config
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from modules.auth.router import router as auth_router
from modules.libtorrent_client.background_tasks import alert_loop, resume_save_loop
from modules.libtorrent_client.dependencies import get_libtorrent_client_service
from modules.monitoring.router import router as monitoring_router
from modules.pairings.background_tasks import run_expired_pairings_cleanup
from modules.pairings.router import router as pairings_router
from modules.persisted_torrents.router import router as torrents_router
from modules.settings.router import router as setting_router
from modules.stream.dependencies import get_stream_service
from modules.stream.router import router as stream_router
from modules.stremio.router import router as stremio_router
from modules.torrent_files.background_tasks import run_torrent_files_retention_cleanup
from modules.torrent_files.router import router as torrent_files_router
from modules.users.router import router as users_router
from setproctitle import setproctitle
from starlette.middleware.sessions import SessionMiddleware

setproctitle("stremhu-source")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.node_env == NodeEnv.PRODUCTION:
        for route in app.routes:
            if isinstance(route, APIRoute):
                is_external = pydash.get(route, "openapi_extra.x-external") is True
                if not is_external:
                    route.include_in_schema = False

    out_dir = config.openapi_dir
    with (out_dir / "openapi.json").open("w", encoding="utf-8") as f:
        json.dump(app.openapi(), f, indent=2, ensure_ascii=False)

    # Beállítások inicializálása az adatbázisban és a libtorrent-ben induláskor
    from common.database import SessionLocal
    from modules.settings.repository import SettingsRepository
    from modules.settings.service import SettingsService

    db = SessionLocal()
    try:
        repository = SettingsRepository(db)
        settings_service = SettingsService(repository, get_libtorrent_client_service())
        settings_service.initialize_defaults()
        db.commit()
    except Exception as e:
        db.rollback()
        import logging

        logging.getLogger("main").error(
            f"Nem sikerült a beállítások inicializálása induláskor: {e}"
        )
    finally:
        db.close()

    # Háttérfeladatok indítása
    alert_task = asyncio.create_task(alert_loop())
    save_task = asyncio.create_task(resume_save_loop())

    # APScheduler ütemező indítása
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_torrent_files_retention_cleanup,
        trigger="cron",
        hour=3,
        minute=0,
        id="torrent_files_cleanup",
        replace_existing=True,
    )
    scheduler.add_job(
        run_expired_pairings_cleanup,
        trigger="cron",
        hour="*",
        minute=0,
        id="expired_pairings_cleanup",
        replace_existing=True,
    )
    scheduler.start()

    libtorrent_client_service = get_libtorrent_client_service()
    stream_service = get_stream_service(
        libtorrent_client_service=libtorrent_client_service
    )
    priority_manager_task = asyncio.create_task(stream_service.priority_manager_loop())

    yield

    priority_manager_task.cancel()
    scheduler.shutdown()
    save_task.cancel()
    alert_task.cancel()

    libtorrent_client_service.trigger_save_resume_data()

    await asyncio.sleep(1)
    libtorrent_client_service.process_alerts()


app = FastAPI(
    title="StremHU Source",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    SessionMiddleware,
    session_cookie="stremhu.source",
    secret_key=config.session_secret,
    max_age=1000 * 60 * 60 * 24 * 30,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(monitoring_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(setting_router)
api_router.include_router(torrents_router)
api_router.include_router(torrent_files_router)
api_router.include_router(stream_router)
api_router.include_router(stremio_router)
api_router.include_router(pairings_router)

app.include_router(api_router)


app.mount(
    "/",
    StaticFiles(
        directory=config.client_path,
        html=True,
    ),
    name="frontend",
)
