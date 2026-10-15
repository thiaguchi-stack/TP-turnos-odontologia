from datetime import datetime

import pytest
from sqlalchemy.exc import StatementError

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Paciente, Prestacion, Profesional, Sillon, Turno
from app.models.turno import ESTADOS_TURNO, EstadoTurno
from app.models.usuario import RolUsuario

FECHA = datetime(2026, 11, 5, 9, 0)
FIN = datetime(2026, 11, 5, 9, 30)


@pytest.fixture(autouse=True)
def _esquema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _turno(db):
    profesional = Profesional(nombre="Ana", apellido="Rivas", especialidad="Ortodoncia")
    paciente = Paciente(
        nombre="Lucía", apellido="Pérez", dni="40111222", telefono="1155551234"
    )
    prestacion = Prestacion(nombre="Limpieza", duracion_minutos=30)
    sillon = Sillon(nombre="Sillón 1")
    db.add_all([profesional, paciente, prestacion, sillon])
    db.commit()
    return Turno(
        profesional_id=profesional.id,
        paciente_id=paciente.id,
        prestacion_id=prestacion.id,
        sillon_id=sillon.id,
        fecha_hora_inicio=FECHA,
        fecha_hora_fin=FIN,
    )


def test_estado_turno_tiene_los_cuatro_valores_exactos():
    assert {estado.value for estado in EstadoTurno} == {
        "reservado",
        "confirmado",
        "cancelado",
        "completado",
    }


def test_estados_turno_se_conserva_como_alias_de_compatibilidad():
    assert ESTADOS_TURNO == ("reservado", "confirmado", "cancelado", "completado")


def test_rol_usuario_tiene_admin_y_odontologo():
    assert {rol.value for rol in RolUsuario} == {"admin", "odontologo"}


def test_estado_turno_fuera_del_enum_no_construye():
    with pytest.raises(ValueError):
        EstadoTurno("reprogramado")


def test_rol_usuario_fuera_del_enum_no_construye():
    with pytest.raises(ValueError):
        RolUsuario("superadmin")


def test_turno_estado_por_defecto_es_reservado():
    with SessionLocal() as db:
        turno = _turno(db)
        db.add(turno)
        db.commit()
        db.refresh(turno)

    assert turno.estado == EstadoTurno.RESERVADO
    assert turno.estado == "reservado"


def test_turno_con_estado_en_texto_fuera_del_enum_no_se_persiste():
    with SessionLocal() as db:
        turno = _turno(db)
        turno.estado = "reprogramado"
        db.add(turno)

        with pytest.raises(StatementError):
            db.flush()

        db.rollback()
