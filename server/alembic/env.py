import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context

# 1. Add 'relay' root directory to Python path so we can import application code
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 2. Import Base and engine from common.database and load application config
# 3. Dynamic model auto-discovery: Auto-import all files named "models.py" under relay root
import importlib
import pkgutil

from common.database import Base, engine
from config import config

root_path = Path(__file__).resolve().parent.parent
for _, module_name, _ in pkgutil.walk_packages([str(root_path)]):
    if "models" in module_name:
        importlib.import_module(module_name)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use dynamic database URL from application config
    url = config.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Directly reuse the application's database engine
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # SQLite safe table modification support
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
