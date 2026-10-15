"""Preparación de la base de datos al arrancar la app.

- Base **en memoria** (tests): se crea el esquema desde ``Base.metadata`` con
  ``create_all`` y no se pasa por Alembic (rápido, sin archivos).
- Base **persistente** (dev/prod): se aplican las migraciones Alembic
  (``upgrade head``), que es la fuente de esquema versionada (OQ-1).
- En ambos casos se corre el seed mínimo idempotente.
"""

from app.core.config import settings
from app.db.base import Base
from app.db.migraciones import aplicar_migraciones
from app.db.seed import seed_minimo
from app.db.session import SessionLocal, engine

_URLS_EN_MEMORIA = {"sqlite://", "sqlite:///:memory:"}


def preparar_base_de_datos() -> None:
    if settings.database_url in _URLS_EN_MEMORIA:
        Base.metadata.create_all(bind=engine)
    else:
        aplicar_migraciones(settings.database_url)

    with SessionLocal() as db:
        seed_minimo(db)
