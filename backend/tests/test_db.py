import os

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import session as session_mod


def test_settings_lee_database_url_del_entorno():
    assert settings.database_url == os.environ["DATABASE_URL"]


def test_engine_sqlite_se_instancia_y_ejecuta():
    with session_mod.engine.connect() as conexion:
        assert conexion.execute(text("SELECT 1")).scalar() == 1


def test_get_db_cierra_la_sesion(monkeypatch):
    generador = session_mod.get_db()
    db = next(generador)

    assert isinstance(db, Session)

    cerro = {"valor": False}
    close_real = db.close

    def close_espia():
        cerro["valor"] = True
        close_real()

    monkeypatch.setattr(db, "close", close_espia)

    with pytest.raises(StopIteration):
        next(generador)

    assert cerro["valor"] is True
