from datetime import datetime

import pytest
from sqlalchemy import func, select

from app.models import Prestacion, Turno
from app.schemas.prestacion import PrestacionCreate, PrestacionUpdate
from app.services import prestacion_service
from app.services.errores import (
    PrestacionNoEncontradaError,
    PrestacionRechazadaError,
)


def test_crear_prestacion_de_30_minutos_queda_activa_y_persistida(db, datos):
    creada = prestacion_service.crear(
        db, PrestacionCreate(nombre="Limpieza", duracion_minutos=30)
    )

    assert creada.id > 0
    assert creada.activa is True
    persistida = db.get(Prestacion, creada.id)
    assert (persistida.nombre, persistida.duracion_minutos) == ("Limpieza", 30)


@pytest.mark.parametrize("duracion", [0, -5])
def test_crear_rechaza_duracion_no_positiva_sin_persistir(db, datos, duracion):
    total_antes = db.scalar(select(func.count()).select_from(Prestacion))

    with pytest.raises(PrestacionRechazadaError, match="mayor que cero"):
        prestacion_service.crear(
            db,
            PrestacionCreate.model_construct(
                nombre="Inválida", duracion_minutos=duracion
            ),
        )

    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Prestacion)) == total_antes


def test_listar_activas_excluye_la_inactiva_y_ordena_por_id(db, datos):
    activas = prestacion_service.listar_activas(db)

    assert [prestacion.id for prestacion in activas] == [
        datos.prestacion_30.id,
        datos.prestacion_45.id,
    ]


def test_listar_activas_incluye_las_creadas_y_excluye_las_dadas_de_baja(db, datos):
    nueva = prestacion_service.crear(
        db, PrestacionCreate(nombre="Ortodoncia", duracion_minutos=50)
    )
    prestacion_service.actualizar(
        db, datos.prestacion_45.id, PrestacionUpdate(activa=False)
    )

    assert [prestacion.id for prestacion in prestacion_service.listar_activas(db)] == [
        datos.prestacion_30.id,
        nueva.id,
    ]


def test_actualizar_cambia_nombre_duracion_y_activa(db, datos):
    actualizada = prestacion_service.actualizar(
        db,
        datos.prestacion_30.id,
        PrestacionUpdate(
            nombre="Limpieza profunda", duracion_minutos=60, activa=False
        ),
    )

    assert (actualizada.nombre, actualizada.duracion_minutos, actualizada.activa) == (
        "Limpieza profunda",
        60,
        False,
    )
    db.expire_all()
    persistida = db.get(Prestacion, datos.prestacion_30.id)
    assert (persistida.nombre, persistida.duracion_minutos, persistida.activa) == (
        "Limpieza profunda",
        60,
        False,
    )
    assert datos.prestacion_30.id not in [
        prestacion.id for prestacion in prestacion_service.listar_activas(db)
    ]

    reactivada = prestacion_service.actualizar(
        db, datos.prestacion_30.id, PrestacionUpdate(activa=True)
    )
    assert reactivada.activa is True
    assert datos.prestacion_30.id in [
        prestacion.id for prestacion in prestacion_service.listar_activas(db)
    ]


@pytest.mark.parametrize("duracion", [0, -5])
def test_actualizar_rechaza_duracion_no_positiva_sin_modificar(db, datos, duracion):
    with pytest.raises(PrestacionRechazadaError, match="mayor que cero"):
        prestacion_service.actualizar(
            db,
            datos.prestacion_30.id,
            PrestacionUpdate.model_construct(duracion_minutos=duracion),
        )

    db.expire_all()
    assert db.get(Prestacion, datos.prestacion_30.id).duracion_minutos == 30


def test_actualizar_id_inexistente_lanza_error_de_dominio(db, datos):
    with pytest.raises(PrestacionNoEncontradaError, match="No existe"):
        prestacion_service.actualizar(
            db, 999999, PrestacionUpdate(nombre="Nora", duracion_minutos=30)
        )

    db.expire_all()
    assert db.get(Prestacion, 999999) is None
    assert db.get(Prestacion, datos.prestacion_30.id).nombre == "Limpieza"


def test_el_servicio_no_toca_turnos_existentes(db, datos):
    inicio = datetime(2026, 11, 5, 9, 0)
    turno = Turno(
        profesional_id=datos.prof_activo.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_1.id,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=inicio.replace(minute=30),
    )
    db.add(turno)
    db.commit()
    fin_original = turno.fecha_hora_fin

    prestacion_service.actualizar(
        db, datos.prestacion_30.id, PrestacionUpdate(duracion_minutos=60, activa=False)
    )

    db.expire_all()
    persistido = db.get(Turno, turno.id)
    assert persistido is not None
    assert persistido.fecha_hora_fin == fin_original
    assert persistido.prestacion_id == datos.prestacion_30.id
