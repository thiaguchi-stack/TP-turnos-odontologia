from datetime import datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Paciente, Prestacion, Profesional, Sillon, Turno

FECHA = datetime(2026, 11, 5, 9, 0)
FIN = datetime(2026, 11, 5, 9, 30)


@pytest.fixture(autouse=True)
def _esquema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _seed_minimo(db):
    profesional = Profesional(nombre="Ana", apellido="Rivas", especialidad="Ortodoncia")
    paciente = Paciente(
        nombre="Lucía", apellido="Pérez", dni="40111222", telefono="1155551234"
    )
    prestacion = Prestacion(nombre="Limpieza", duracion_minutos=30)
    sillon = Sillon(nombre="Sillón 1")
    db.add_all([profesional, paciente, prestacion, sillon])
    db.commit()
    return (profesional.id, paciente.id, prestacion.id, sillon.id)


def test_paciente_mismo_dni_telefono_rechazado():
    with SessionLocal() as db:
        p1 = Paciente(nombre="A", apellido="B", dni="11111111", telefono="123")
        db.add(p1)
        db.commit()
        p2 = Paciente(nombre="C", apellido="D", dni="11111111", telefono="123")
        db.add(p2)
        with pytest.raises(IntegrityError):
            db.commit()


def test_paciente_mismo_dni_telefono_distinto_permitido():
    with SessionLocal() as db:
        p1 = Paciente(nombre="A", apellido="B", dni="11111111", telefono="123")
        db.add(p1)
        db.commit()
        p2 = Paciente(nombre="C", apellido="D", dni="11111111", telefono="124")
        db.add(p2)
        db.commit()


def test_turno_token_cancelacion_duplicado_rechazado():
    with SessionLocal() as db:
        prof, pac, prest, sillon = _seed_minimo(db)
        t1 = Turno(
            profesional_id=prof,
            paciente_id=pac,
            prestacion_id=prest,
            sillon_id=sillon,
            fecha_hora_inicio=FECHA,
            fecha_hora_fin=FIN,
            token_cancelacion="abc123",
        )
        db.add(t1)
        db.commit()
        t2 = Turno(
            profesional_id=prof,
            paciente_id=pac,
            prestacion_id=prest,
            sillon_id=sillon,
            fecha_hora_inicio=FECHA.replace(day=6),
            fecha_hora_fin=FIN.replace(day=6),
            token_cancelacion="abc123",
        )
        db.add(t2)
        with pytest.raises(IntegrityError):
            db.commit()


def test_turno_token_cancelacion_nulo_permitido():
    with SessionLocal() as db:
        prof, pac, prest, sillon = _seed_minimo(db)
        t1 = Turno(
            profesional_id=prof,
            paciente_id=pac,
            prestacion_id=prest,
            sillon_id=sillon,
            fecha_hora_inicio=FECHA,
            fecha_hora_fin=FIN,
            token_cancelacion=None,
        )
        t2 = Turno(
            profesional_id=prof,
            paciente_id=pac,
            prestacion_id=prest,
            sillon_id=sillon,
            fecha_hora_inicio=FECHA.replace(day=6),
            fecha_hora_fin=FIN.replace(day=6),
            token_cancelacion=None,
        )
        db.add_all([t1, t2])
        db.commit()


def test_indices_turno_y_bloqueo_existen():
    inspector = inspect(engine)
    nombres_turno = {indice["name"] for indice in inspector.get_indexes("turno")}
    assert "ix_turno_profesional_inicio" in nombres_turno
    assert "ix_turno_sillon_inicio" in nombres_turno

    nombres_bloqueo = {indice["name"] for indice in inspector.get_indexes("bloqueo")}
    assert "ix_bloqueo_profesional_inicio" in nombres_bloqueo
