import sys
from pathlib import Path

# Biztosítjuk, hogy a gyökér könyvtár benne legyen a Python keresési útvonalában
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn
from alembic import command
from alembic.config import Config
from config import NodeEnv, config


def setup_directories():
    print("🔄 Szükséges könyvtárstruktúra ellenőrzése és létrehozása...")

    config.downloads_dir.mkdir(parents=True, exist_ok=True)
    config.openapi_dir.mkdir(parents=True, exist_ok=True)
    config.client_path.mkdir(parents=True, exist_ok=True)


def run_migrations():
    print("🔄 Adatbázis-migrációk ellenőrzése és futtatása...")

    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"[HIBA] Nem sikerült lefutattatni a migrációkat: {e}", file=sys.stderr)
        sys.exit(1)


def start_server():
    print(f"🚀 Uvicorn szerver indítása a(z) {config.port} porton...")

    is_dev = config.node_env == NodeEnv.DEVELOPMENT
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.port,
        reload=is_dev,
    )


if __name__ == "__main__":
    setup_directories()
    run_migrations()
    start_server()
