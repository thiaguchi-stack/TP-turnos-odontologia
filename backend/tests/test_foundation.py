import importlib

from fastapi.testclient import TestClient

from app.core import security
from app.core.config import Settings, settings
from app.main import app


def test_security_stub_importa_sin_error():
    modulo = importlib.import_module("app.core.security")

    assert modulo is not None


def test_security_stub_lee_secret_key_de_config(monkeypatch):
    monkeypatch.setattr(settings, "secret_key", "valor-de-prueba")

    assert security.get_secret_key() == "valor-de-prueba"


def test_cors_default_incluye_localhost_frontend(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    ajustes = Settings(_env_file=None)

    assert isinstance(ajustes.cors_origins, list)
    assert "http://localhost:5173" in ajustes.cors_origins


def test_cors_origins_parsea_lista_separada_por_coma(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test, http://b.test")

    ajustes = Settings(_env_file=None)

    assert ajustes.cors_origins == ["http://a.test", "http://b.test"]


def test_cors_middleware_permite_origen_configurado():
    with TestClient(app) as client:
        respuesta = client.get(
            "/api/health", headers={"Origin": "http://localhost:5173"}
        )

    assert respuesta.status_code == 200
    assert (
        respuesta.headers.get("access-control-allow-origin") == "http://localhost:5173"
    )


def test_cors_middleware_omite_origen_no_permitido():
    with TestClient(app) as client:
        respuesta = client.get(
            "/api/health", headers={"Origin": "http://sitio-no-permitido.test"}
        )

    assert respuesta.status_code == 200
    assert "access-control-allow-origin" not in respuesta.headers
