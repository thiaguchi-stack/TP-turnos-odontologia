import sqlite3
from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _set_sqlite_fk_on_connect(dbapi_connection: Any, _connection_record: Any) -> None:
    """Activa ``PRAGMA foreign_keys=ON`` en cada conexión SQLite.

    SQLite no aplica las FKs por defecto; sin esto las restricciones de
    integridad referencial (p. ej. ``Usuario.profesional_id``) no se validan.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def _crear_engine(url: str) -> Engine:
    if url in {"sqlite://", "sqlite:///:memory:"}:
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(url)

    event.listen(engine, "connect", _set_sqlite_fk_on_connect)
    return engine


engine = _crear_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
