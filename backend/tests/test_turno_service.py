from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.models import Bloqueo, Profesional, Turno
from app.services.errores import TurnoRechazadoError, TurnoSolapadoError
from app.services.turno_service import crear_turno

FECHA = datetime(2026, 11, 5, 9, 0)


def _crear(db, datos, *, inicio=FECHA, sillon=None, profesional=None, prestacion=None):
    return crear_turno(
        db,
        profesional_id=(profesional or datos.prof_activo).id,
        paciente_id=datos.paciente.id,
        prestacion_id=(prestacion or datos.prestacion_30).id,
        sillon_id=(sillon or datos.sillon_1).id,
        fecha_hora_inicio=inicio,
    )


def _rechazo(db, datos, **kwargs):
    with pytest.raises(TurnoRechazadoError) as excinfo:
        _crear(db, datos, **kwargs)
    return excinfo.value


# 3.2 — Caso feliz: duración derivada + estado reservado


def test_turno_feliz_con_fin_derivado_y_estado_reservado(db, datos):
    turno = _crear(db, datos)

    assert turno.id is not None
    assert turno.fecha_hora_inicio == datetime(2026, 11, 5, 9, 0)
    assert turno.fecha_hora_fin == datetime(2026, 11, 5, 9, 30)
    assert turno.estado == "reservado"
    assert turno.sillon_id == datos.sillon_1.id


def test_duracion_derivada_respeta_minutos_de_la_prestacion(db, datos):
    turno = _crear(db, datos, prestacion=datos.prestacion_45)

    assert turno.fecha_hora_fin == datetime(2026, 11, 5, 9, 45)


def test_crear_turno_no_acepta_estado_ni_fecha_hora_fin(db, datos):
    base = dict(
        db=db,
        profesional_id=datos.prof_activo.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_1.id,
        fecha_hora_inicio=FECHA,
    )

    with pytest.raises(TypeError):
        crear_turno(**base, estado="confirmado")
    with pytest.raises(TypeError):
        crear_turno(**base, fecha_hora_fin=datetime(2026, 11, 5, 9, 30))


# 3.3 — Solapamiento (RN-TU-01, RN-PR-03, RN-PR-05)


def test_colision_por_profesional_con_sillon_distinto(db, datos):
    _crear(db, datos, inicio=datetime(2026, 11, 5, 9, 0), sillon=datos.sillon_1)

    with pytest.raises(TurnoSolapadoError) as excinfo:
        _crear(db, datos, inicio=datetime(2026, 11, 5, 9, 15), sillon=datos.sillon_2)

    assert excinfo.value.motivo == "profesional"


def test_colision_por_sillon_con_profesional_distinto(db, datos):
    segundo = Profesional(nombre="Carla", apellido="Méndez", especialidad="Cirugía")
    db.add(segundo)
    db.commit()
    db.refresh(segundo)

    _crear(db, datos, inicio=datetime(2026, 11, 5, 9, 0), sillon=datos.sillon_1)

    with pytest.raises(TurnoSolapadoError) as excinfo:
        _crear(
            db,
            datos,
            inicio=datetime(2026, 11, 5, 9, 20),
            sillon=datos.sillon_1,
            profesional=segundo,
        )

    assert excinfo.value.motivo == "sillón"


def test_colision_con_bloqueo_de_sillon_nulo(db, datos):
    db.add(
        Bloqueo(
            profesional_id=datos.prof_activo.id,
            sillon_id=None,
            fecha_hora_inicio=datetime(2026, 11, 5, 15, 0),
            fecha_hora_fin=datetime(2026, 11, 5, 19, 0),
        )
    )
    db.commit()

    with pytest.raises(TurnoSolapadoError) as excinfo:
        _crear(db, datos, inicio=datetime(2026, 11, 5, 16, 0))

    assert excinfo.value.motivo == "bloqueo"


def test_colision_con_bloqueo_del_mismo_sillon(db, datos):
    db.add(
        Bloqueo(
            profesional_id=datos.prof_activo.id,
            sillon_id=datos.sillon_1.id,
            fecha_hora_inicio=datetime(2026, 11, 5, 15, 0),
            fecha_hora_fin=datetime(2026, 11, 5, 19, 0),
        )
    )
    db.commit()

    with pytest.raises(TurnoSolapadoError) as excinfo:
        _crear(db, datos, inicio=datetime(2026, 11, 5, 16, 0), sillon=datos.sillon_1)

    assert excinfo.value.motivo == "bloqueo"


def test_bloqueo_de_un_sillon_no_afecta_a_otro_sillon(db, datos):
    db.add(
        Bloqueo(
            profesional_id=datos.prof_activo.id,
            sillon_id=datos.sillon_1.id,
            fecha_hora_inicio=datetime(2026, 11, 5, 15, 0),
            fecha_hora_fin=datetime(2026, 11, 5, 19, 0),
        )
    )
    db.commit()

    turno = _crear(
        db, datos, inicio=datetime(2026, 11, 5, 16, 0), sillon=datos.sillon_2
    )

    assert turno.id is not None


def test_bloqueo_de_otro_profesional_no_afecta(db, datos):
    segundo = Profesional(nombre="Carla", apellido="Méndez", especialidad="Cirugía")
    db.add(segundo)
    db.commit()
    db.refresh(segundo)

    db.add(
        Bloqueo(
            profesional_id=segundo.id,
            sillon_id=None,
            fecha_hora_inicio=datetime(2026, 11, 5, 15, 0),
            fecha_hora_fin=datetime(2026, 11, 5, 19, 0),
        )
    )
    db.commit()

    turno = _crear(db, datos, inicio=datetime(2026, 11, 5, 16, 0))

    assert turno.id is not None


def test_borde_inicio_exactamente_al_fin_es_permitido(db, datos):
    _crear(db, datos, inicio=datetime(2026, 11, 5, 9, 0), sillon=datos.sillon_1)

    turno = _crear(
        db, datos, inicio=datetime(2026, 11, 5, 9, 30), sillon=datos.sillon_1
    )

    assert turno.id is not None
    assert turno.fecha_hora_inicio == datetime(2026, 11, 5, 9, 30)


def test_borde_inicio_un_minuto_antes_del_fin_es_rechazado(db, datos):
    _crear(db, datos, inicio=datetime(2026, 11, 5, 9, 0), sillon=datos.sillon_1)

    with pytest.raises(TurnoSolapadoError):
        _crear(db, datos, inicio=datetime(2026, 11, 5, 9, 29), sillon=datos.sillon_1)


def test_turno_cancelado_no_bloquea_la_agenda(db, datos):
    turno_previo = _crear(db, datos, inicio=datetime(2026, 11, 5, 9, 0))

    turno_previo.estado = "cancelado"
    db.commit()

    turno_nuevo = _crear(db, datos, inicio=datetime(2026, 11, 5, 9, 10))

    assert turno_nuevo.id is not None
    assert turno_nuevo.estado == "reservado"


# 3.4 — Elegibilidad (RN-PR-01/02, RN-TU-06/09, FKs)


def test_turno_en_el_pasado_es_rechazado(db, datos):
    error = _rechazo(db, datos, inicio=datetime.now() - timedelta(hours=1))
    assert "pasado" in error.motivo.lower()


# RN-TU-06 — interpretación: "pasado" se juzga al momento de INICIAR
# (spec «Sin turnos en el pasado»: fecha_hora_inicio anterior a ahora)


def test_turno_en_curso_inicio_en_pasado_y_fin_en_futuro_es_rechazado(db, datos):
    ahora = datetime(2030, 6, 1, 12, 0)
    with patch("app.core.clock.now", return_value=ahora):
        error = _rechazo(db, datos, inicio=datetime(2030, 6, 1, 11, 40))

    # inicio 11:40 < ahora, pero el fin derivado (12:10) aún no pasó
    assert "pasado" in error.motivo.lower()


def test_turno_con_fin_ya_pasado_es_rechazado(db, datos):
    ahora = datetime(2030, 6, 1, 12, 0)
    with patch("app.core.clock.now", return_value=ahora):
        error = _rechazo(db, datos, inicio=datetime(2030, 6, 1, 11, 0))

    # inicio 11:00 y fin derivado 11:30 < ahora: ambas lecturas coinciden
    assert "pasado" in error.motivo.lower()


def test_inicio_exactamente_igual_al_ahora_es_aceptado(db, datos):
    ahora = datetime(2030, 6, 1, 12, 0)
    with patch("app.core.clock.now", return_value=ahora):
        turno = _crear(db, datos, inicio=ahora)

    assert turno.id is not None
    assert turno.estado == "reservado"


def test_profesional_inactivo_es_rechazado(db, datos):
    error = _rechazo(db, datos, profesional=datos.prof_inactivo)
    assert "profesional" in error.motivo.lower()
    assert "inactivo" in error.motivo.lower()


def test_sillon_inactivo_es_rechazado(db, datos):
    error = _rechazo(db, datos, sillon=datos.sillon_inactivo)
    assert "sillón" in error.motivo.lower()


def test_prestacion_inactiva_es_rechazada(db, datos):
    error = _rechazo(db, datos, prestacion=datos.prestacion_inactiva)
    assert "prestación" in error.motivo.lower()
    assert "inactiva" in error.motivo.lower()


@pytest.mark.parametrize(
    "campo,valor",
    [
        ("profesional_id", 9999),
        ("paciente_id", 9999),
        ("prestacion_id", 9999),
        ("sillon_id", 9999),
    ],
)
def test_fk_inexistente_es_rechazado(db, datos, campo, valor):
    kwargs = dict(
        profesional_id=datos.prof_activo.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_1.id,
        fecha_hora_inicio=FECHA,
    )
    kwargs[campo] = valor

    with pytest.raises(TurnoRechazadoError) as excinfo:
        crear_turno(db, **kwargs)

    assert "no existe" in excinfo.value.motivo.lower()


def test_fk_inexistente_no_deja_registros_en_turno(db, datos):
    try:
        crear_turno(
            db,
            profesional_id=9999,
            paciente_id=datos.paciente.id,
            prestacion_id=datos.prestacion_30.id,
            sillon_id=datos.sillon_1.id,
            fecha_hora_inicio=FECHA,
        )
    except TurnoRechazadoError:
        pass

    assert len(db.query(Turno).all()) == 0
