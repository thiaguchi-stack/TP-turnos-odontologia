import os
from collections.abc import Iterator
from types import SimpleNamespace

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine, get_db
from app.main import app
from app.models import Paciente, Prestacion, Profesional, Sillon


def _seed_datos_base(db: Session) -> SimpleNamespace:
    prof_activo = Profesional(nombre="Ana", apellido="Rivas", especialidad="Ortodoncia")
    prof_inactivo = Profesional(
        nombre="Jorge", apellido="Luna", especialidad="Endodoncia", activo=False
    )
    sillon_1 = Sillon(nombre="Sillón 1")
    sillon_2 = Sillon(nombre="Sillón 2")
    sillon_inactivo = Sillon(nombre="Sillón 3", activo=False)
    prestacion_30 = Prestacion(nombre="Limpieza", duracion_minutos=30)
    prestacion_45 = Prestacion(nombre="Obturación", duracion_minutos=45)
    prestacion_inactiva = Prestacion(
        nombre="Extracción", duracion_minutos=60, activa=False
    )
    paciente = Paciente(
        nombre="Lucía",
        apellido="Pérez",
        dni="40111222",
        telefono="1155551234",
    )

    db.add_all(
        [
            prof_activo,
            prof_inactivo,
            sillon_1,
            sillon_2,
            sillon_inactivo,
            prestacion_30,
            prestacion_45,
            prestacion_inactiva,
            paciente,
        ]
    )
    db.commit()

    objetos = [
        prof_activo,
        prof_inactivo,
        sillon_1,
        sillon_2,
        sillon_inactivo,
        prestacion_30,
        prestacion_45,
        prestacion_inactiva,
        paciente,
    ]
    for obj in objetos:
        db.refresh(obj)

    return SimpleNamespace(
        prof_activo=prof_activo,
        prof_inactivo=prof_inactivo,
        sillon_1=sillon_1,
        sillon_2=sillon_2,
        sillon_inactivo=sillon_inactivo,
        prestacion_30=prestacion_30,
        prestacion_45=prestacion_45,
        prestacion_inactiva=prestacion_inactiva,
        paciente=paciente,
    )


@pytest.fixture
def db() -> Iterator[Session]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    sesion = SessionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def datos(db: Session) -> SimpleNamespace:
    return _seed_datos_base(db)


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    def _override_get_db() -> Iterator[Session]:
        sesion = SessionLocal()
        try:
            yield sesion
        finally:
            sesion.close()

    app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(app) as cliente:
            yield cliente
    finally:
        app.dependency_overrides.pop(get_db, None)
