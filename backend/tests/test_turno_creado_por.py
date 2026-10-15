from datetime import datetime

import pytest

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Paciente, Prestacion, Profesional, Sillon, Turno, Usuario
from app.models.usuario import RolUsuario

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


def test_turno_creado_por_es_nulo_por_defecto_reserva_online():
    with SessionLocal() as db:
        prof, pac, prest, sillon = _seed_minimo(db)
        turno = Turno(
            profesional_id=prof,
            paciente_id=pac,
            prestacion_id=prest,
            sillon_id=sillon,
            fecha_hora_inicio=FECHA,
            fecha_hora_fin=FIN,
        )
        db.add(turno)
        db.commit()
        db.refresh(turno)

    assert turno.creado_por is None


def test_turno_creado_por_acepta_fk_a_usuario_existente():
    with SessionLocal() as db:
        prof, pac, prest, sillon = _seed_minimo(db)
        admin = Usuario(
            email="admin@clinica.local",
            password_hash="hash",
            rol=RolUsuario.ADMIN,
        )
        db.add(admin)
        db.commit()
        admin_id = admin.id

        turno = Turno(
            profesional_id=prof,
            paciente_id=pac,
            prestacion_id=prest,
            sillon_id=sillon,
            fecha_hora_inicio=FECHA,
            fecha_hora_fin=FIN,
            creado_por=admin_id,
        )
        db.add(turno)
        db.commit()
        db.refresh(turno)

    assert turno.creado_por == admin_id
