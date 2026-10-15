from datetime import datetime
from unittest.mock import patch

import pytest

from app.models import Paciente, Turno
from app.services.errores import TurnoRechazadoError
from app.services.turno_service import crear_turno

FUTURO = datetime(2030, 6, 1, 12, 0)
PASADO = datetime(2020, 1, 1, 12, 0)


def _crear(db, datos, inicio):
    return crear_turno(
        db,
        profesional_id=datos.prof_activo.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_1.id,
        fecha_hora_inicio=inicio,
    )


# Convención del reloj central: hora local naive (sin tzinfo)


def test_now_devuelve_hora_local_naive():
    from app.core import clock

    actual = clock.now()

    assert isinstance(actual, datetime)
    assert actual.tzinfo is None
    assert abs((datetime.now() - actual).total_seconds()) < 5


# call site 1 — turno_service.crear_turno usa el reloj central


def test_crear_turno_rechaza_inicio_anterior_al_reloj_central(db, datos):
    with patch("app.core.clock.now", return_value=FUTURO):
        with pytest.raises(TurnoRechazadoError) as excinfo:
            _crear(db, datos, inicio=datetime(2030, 6, 1, 11, 0))

    assert "pasado" in excinfo.value.motivo.lower()


def test_crear_turno_acepta_inicio_posterior_al_reloj_central(db, datos):
    with patch("app.core.clock.now", return_value=PASADO):
        turno = _crear(db, datos, inicio=datetime(2020, 1, 1, 13, 0))

    assert turno.id is not None
    assert turno.estado == "reservado"


# call sites 2 y 3 — defaults `creado_en` de los modelos


def test_creado_en_del_turno_usa_el_reloj_central(db, datos):
    fijo = datetime(2026, 1, 1, 12, 0)

    with patch("app.core.clock.now", return_value=fijo):
        turno = Turno(
            profesional_id=datos.prof_activo.id,
            paciente_id=datos.paciente.id,
            prestacion_id=datos.prestacion_30.id,
            sillon_id=datos.sillon_1.id,
            fecha_hora_inicio=datetime(2026, 11, 5, 9, 0),
            fecha_hora_fin=datetime(2026, 11, 5, 9, 30),
        )
        db.add(turno)
        db.commit()
        db.refresh(turno)

    assert turno.creado_en == fijo


def test_creado_en_del_paciente_usa_el_reloj_central(db, datos):
    fijo = datetime(2026, 1, 1, 12, 0)

    with patch("app.core.clock.now", return_value=fijo):
        paciente = Paciente(
            nombre="Martín",
            apellido="Sosa",
            dni="35999888",
            telefono="1166667777",
        )
        db.add(paciente)
        db.commit()
        db.refresh(paciente)

    assert paciente.creado_en == fijo
