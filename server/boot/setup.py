import sys

from alembic import command
from alembic.config import Config
from config import config


def setup_directories():
    print("🔄 Szükséges könyvtárstruktúra ellenőrzése és létrehozása...")

    config.openapi_dir.mkdir(parents=True, exist_ok=True)
    config.client_path.mkdir(parents=True, exist_ok=True)

    config.downloads_dir.mkdir(parents=True, exist_ok=True)
    config.generated_certificates_dir.mkdir(parents=True, exist_ok=True)
    config.own_certificates_dir.mkdir(parents=True, exist_ok=True)


def run_migrations():
    print("🔄 Adatbázis-migrációk ellenőrzése és futtatása...")

    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"[HIBA] Nem sikerült lefutattatni a migrációkat: {e}", file=sys.stderr)
        sys.exit(1)
