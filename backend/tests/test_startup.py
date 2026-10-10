from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.db.session import engine
from app.main import app


def test_app_arranca_y_crea_las_tablas_en_memoria():
    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200

    inspector = inspect(engine)
    assert inspector.has_table("turno")
    assert inspector.has_table("bloqueo")
    assert inspector.has_table("profesional")
    assert inspector.has_table("paciente")
    assert inspector.has_table("prestacion")
    assert inspector.has_table("sillon")
