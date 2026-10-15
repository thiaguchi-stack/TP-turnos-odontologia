from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app import models  # noqa: F401  (registra los modelos en la metadata)
from app.db.base import Base

DIRECTORIO_BACKEND = Path(__file__).resolve().parents[1]


def _config(url: str) -> Config:
    config = Config(str(DIRECTORIO_BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(DIRECTORIO_BACKEND / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    return config


def _url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'migracion.db'}"


def test_esquema_migrado_coincide_con_metadata(tmp_path: Path):
    url = _url(tmp_path)
    command.upgrade(_config(url), "head")

    engine = create_engine(url)
    inspector = inspect(engine)
    try:
        tablas_metadata = set(Base.metadata.tables)
        tablas_migradas = set(inspector.get_table_names())
        assert tablas_metadata <= tablas_migradas

        for nombre in sorted(tablas_metadata):
            tabla_metadata = Base.metadata.tables[nombre]
            columnas_metadata = {col.name for col in tabla_metadata.columns}
            columnas_migradas = {
                col["name"] for col in inspector.get_columns(nombre)
            }
            assert columnas_metadata == columnas_migradas

            indices_metadata = {
                indice.name for indice in Base.metadata.tables[nombre].indexes
            }
            indices_migrados = {
                indice["name"] for indice in inspector.get_indexes(nombre)
            }
            assert indices_metadata <= indices_migrados
    finally:
        engine.dispose()


def test_downgrade_base_elimina_todas_las_tablas(tmp_path: Path):
    url = _url(tmp_path)
    config = _config(url)
    command.upgrade(config, "head")
    command.downgrade(config, "base")

    engine = create_engine(url)
    inspector = inspect(engine)
    try:
        tablas_restantes = set(inspector.get_table_names())
        assert not (set(Base.metadata.tables) & tablas_restantes)
    finally:
        engine.dispose()
