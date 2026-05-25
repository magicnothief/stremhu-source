from contextlib import contextmanager
from typing import Generator

from config import config
from sqlalchemy import MetaData, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Session, sessionmaker

# Naming convention is CRITICAL for SQLite migrations in Alembic
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(MappedAsDataclass, DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


connect_args = {"check_same_thread": False}
engine = create_engine(config.database_url, connect_args=connect_args)


# Biztosítjuk a Foreign Key megszorítások bekapcsolását minden SQLite kapcsolatnál
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Standard Python környezetkezelő (Context Manager) adatbázis tranzakciókhoz.
    Automatikusan kezeli a commit, rollback és close életciklusokat.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI specifikus függőség-injektor generátor.
    A háttérben biztonságosan delegál a db_session környezetkezelőnek.
    """
    with db_session() as db:
        yield db
