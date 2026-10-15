from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Paciente, Prestacion, Profesional, Sillon, Turno, Usuario
from app.models.usuario import RolUsuario

FECHA = datetime(2026, 11, 5, 9, 0)
FIN = datetime(2026, 11, 5, 9, 30)
FIJO = datetime(2026, 1, 1, 12, 0)


@pytest.fixture(autouse=True)
def _esquema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _seed_minimo(db: Session) -> tuple[int, int, int, int]:
    profesional = Profesional(nombre="Ana", apellido="Rivas", especialidad="Ortodoncia")
    paciente = Paciente(
        nombre="Lucía", apellido="Pérez", dni="40111222", telefono="1155551234"
    )
    prestacion = Prestacion(nombre="Limpieza", duracion_minutos=30)
    sillon = Sillon(nombre="Sillón 1")
    db.add_all([profesional, paciente, prestacion, sillon])
    db.commit()
    return (
        profesional.id,
        paciente.id,
        prestacion.id,
        sillon.id,
    )


def test_creado_en_usuario_automatico_sin_enviarlo():
    with patch("app.core.clock.now", return_value=FIJO):
        with SessionLocal() as db:
            usuario = Usuario(
                email="admin@clinica.local",
                password_hash="pbkdf2$100000$sal$hash",
                rol=RolUsuario.ADMIN,
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)

    assert usuario.creado_en == FIJO


def test_creado_en_paciente_automatico_sin_enviarlo():
    with patch("app.core.clock.now", return_value=FIJO):
        with SessionLocal() as db:
            paciente = Paciente(
                nombre="Martín",
                apellido="Sosa",
                dni="35999888",
                telefono="1166667777",
            )
            db.add(paciente)
            db.commit()
            db.refresh(paciente)

    assert paciente.creado_en == FIJO


def test_creado_en_turno_automatico_sin_enviarlo():
    with patch("app.core.clock.now", return_value=FIJO):
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

    assert turno.creado_en == FIJO
