from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.turno import TurnoCreate, TurnoRead

FECHA = datetime(2026, 11, 5, 9, 0)


def _payload(**extra):
    datos = {
        "profesional_id": 1,
        "paciente_id": 2,
        "prestacion_id": 3,
        "sillon_id": 4,
        "fecha_hora_inicio": FECHA,
    }
    datos.update(extra)
    return datos


def test_turno_create_acepta_exactamente_los_cinco_campos():
    creado = TurnoCreate(**_payload())

    assert creado.profesional_id == 1
    assert creado.paciente_id == 2
    assert creado.prestacion_id == 3
    assert creado.sillon_id == 4
    assert creado.fecha_hora_inicio == FECHA


def test_turno_create_rechaza_campo_estado():
    with pytest.raises(ValidationError):
        TurnoCreate(**{"estado": "confirmado", **_payload()})


def test_turno_create_rechaza_campo_fecha_hora_fin():
    with pytest.raises(ValidationError):
        TurnoCreate(**{"fecha_hora_fin": FECHA, **_payload()})


def test_turno_create_rechaza_campo_desconocido():
    with pytest.raises(ValidationError):
        TurnoCreate(**{"campo_inventado": 1, **_payload()})


def test_turno_read_expone_fecha_hora_fin_y_estado():
    turno = TurnoRead(
        id=7,
        profesional_id=1,
        paciente_id=2,
        prestacion_id=3,
        sillon_id=4,
        fecha_hora_inicio=FECHA,
        fecha_hora_fin=datetime(2026, 11, 5, 9, 30),
        estado="reservado",
    )

    assert turno.fecha_hora_fin == datetime(2026, 11, 5, 9, 30)
    assert turno.estado == "reservado"


def test_turno_read_se_puede_construir_desde_objeto_orm(datos):
    from datetime import datetime as dt

    from app.models import Turno

    modelo = Turno(
        id=1,
        profesional_id=datos.prof_activo.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_1.id,
        fecha_hora_inicio=dt(2026, 11, 5, 9, 0),
        fecha_hora_fin=dt(2026, 11, 5, 9, 30),
        estado="reservado",
    )

    turno = TurnoRead.model_validate(modelo)
    assert turno.estado == "reservado"
    assert turno.fecha_hora_fin == dt(2026, 11, 5, 9, 30)
