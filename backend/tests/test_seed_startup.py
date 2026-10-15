from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.seed import EMAIL_ADMIN, EMAIL_ODONTOLOGO
from app.main import app
from app.models import Usuario


def _cantidad_usuarios(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Usuario)) or 0


def test_startup_siembra_la_base_y_health_responde_200(client, db):
    assert client.get("/api/health").status_code == 200

    db.expire_all()
    assert _cantidad_usuarios(db) == 2
    assert db.scalar(select(Usuario).where(Usuario.email == EMAIL_ADMIN)) is not None
    assert (
        db.scalar(select(Usuario).where(Usuario.email == EMAIL_ODONTOLOGO)) is not None
    )


def test_segundo_arranque_no_duplica_la_siembra(client, db):
    with TestClient(app) as segundo:
        assert segundo.get("/api/health").status_code == 200

    db.expire_all()
    assert _cantidad_usuarios(db) == 2
