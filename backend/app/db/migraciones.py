"""Aplica las migraciones Alembic al esquema configurado.

Es la contraparte *programática* del comando ``alembic upgrade head``: permite
que el ``lifespan`` de la app deje la base de datos (archivo SQLite o Postgres)
al día sin depender de que el desarrollador corra el CLI a mano.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config

#: Raíz del backend (``backend/``), donde viven ``alembic.ini`` y ``alembic/``.
DIRECTORIO_BACKEND = Path(__file__).resolve().parents[2]


def aplicar_migraciones(url: str) -> None:
    """Corre ``upgrade head`` sobre ``url`` con la config del proyecto."""
    config = Config(str(DIRECTORIO_BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(DIRECTORIO_BACKEND / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
