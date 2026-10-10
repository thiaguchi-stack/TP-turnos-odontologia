from datetime import datetime

import pytest
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Bloqueo, Paciente, Prestacion, Profesional, Sillon, Turno

FECHA = datetime(2026, 11, 5, 9, 0)
FIN = datetime(2026, 11, 5, 9, 30)


@pytest.fixture(autouse=True)
def _esquema_a_mano():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _seed_minimo(db: Session) -> tuple[int, int, int, int]:
    profesional = Profesional(nombre="Ana", apellido="Rivas", especialidad="Ortodoncia")
    paciente = Paciente(
        nombre="Lucía",
        apellido="Pérez",
        dni="40111222",
        telefono="1155551234",
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


def test_profesional_persiste_con_activo_true_por_defecto():
    with SessionLocal() as db:
        profesional = Profesional(
            nombre="Ana", apellido="Rivas", especialidad="Ortodoncia"
        )
        db.add(profesional)
        db.commit()
        db.refresh(profesional)

    assert profesional.activo is True
    assert profesional.id is not None


def test_prestacion_persiste_activa_y_con_duracion():
    with SessionLocal() as db:
        prestacion = Prestacion(nombre="Limpieza", duracion_minutos=30)
        db.add(prestacion)
        db.commit()
        db.refresh(prestacion)

    assert prestacion.activa is True
    assert prestacion.duracion_minutos == 30


def test_sillon_persiste_con_activo_true_por_defecto():
    with SessionLocal() as db:
        sillon = Sillon(nombre="Sillón 1")
        db.add(sillon)
        db.commit()
        db.refresh(sillon)

    assert sillon.activo is True


def test_turno_persiste_con_estado_reservado_por_defecto():
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

        assert turno.estado == "reservado"
        assert turno.token_cancelacion is None
        assert turno.cancelado_en is None
        assert turno.motivo_cancelacion is None
        assert turno.creado_en is not None


def test_turno_estado_restringido_a_valores_del_enum():
    columna = Turno.__table__.c.estado
    assert set(columna.type.enums) == {
        "reservado",
        "confirmado",
        "cancelado",
        "completado",
    }


def test_turno_con_estado_invalido_no_se_persiste():
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
        turno.estado = "inventado"
        db.add(turno)

        with pytest.raises(StatementError):
            db.flush()

        db.rollback()


def test_turno_sillon_id_es_not_null_y_fk():
    columna = Turno.__table__.c.sillon_id
    assert columna.nullable is False
    assert any("sillon" in str(fk.target_fullname) for fk in columna.foreign_keys)


def test_turno_fecha_hora_fin_es_not_null():
    assert Turno.__table__.c.fecha_hora_fin.nullable is False


def test_bloqueo_persiste_con_sillon_id_nulo():
    with SessionLocal() as db:
        profesional = Profesional(
            nombre="Ana", apellido="Rivas", especialidad="Ortodoncia"
        )
        db.add(profesional)
        db.commit()

        bloqueo = Bloqueo(
            profesional_id=profesional.id,
            fecha_hora_inicio=datetime(2026, 11, 5, 15, 0),
            fecha_hora_fin=datetime(2026, 11, 5, 19, 0),
        )
        db.add(bloqueo)
        db.commit()
        db.refresh(bloqueo)

        assert bloqueo.sillon_id is None
        assert bloqueo.motivo is None
        assert Bloqueo.__table__.c.sillon_id.nullable is True


def test_paciente_stub_con_datos_de_contacto():
    paciente = Paciente(
        nombre="Lucía",
        apellido="Pérez",
        dni="40111222",
        telefono="1155551234",
    )
    assert paciente.email is None
    assert paciente.obsocial is None
    assert paciente.id is None
