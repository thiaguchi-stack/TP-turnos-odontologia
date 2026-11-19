from pathlib import Path

from app.core import security
from app.core.config import Settings

ENV_EXAMPLE = Path(__file__).parents[1].joinpath(".env.example")


def test_default_de_expiracion_es_480_y_env_example_alineado():
    assert Settings(_env_file=None).token_expire_min == 480
    assert "TOKEN_EXPIRE_MIN=480" in ENV_EXAMPLE.read_text(encoding="utf-8")


def test_seguridad_toma_secret_key_y_expiracion_del_entorno(monkeypatch):
    clave = "clave-ficticia-de-entorno-con-longitud-suficiente"
    monkeypatch.setenv("SECRET_KEY", clave)
    monkeypatch.setenv("TOKEN_EXPIRE_MIN", "17")

    ajustes = Settings(_env_file=None)

    assert ajustes.secret_key == clave
    assert ajustes.token_expire_min == 17

    monkeypatch.setattr(security.settings, "secret_key", ajustes.secret_key)
    monkeypatch.setattr(
        security.settings, "token_expire_min", ajustes.token_expire_min
    )

    assert security.get_secret_key() == clave
    assert security.get_token_expire_min() == 17
