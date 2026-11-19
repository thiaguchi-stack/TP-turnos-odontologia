from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select

from app.core import security
from app.models import Profesional, Turno, Usuario
from app.models.usuario import RolUsuario
from app.schemas.profesional import ProfesionalCreate, ProfesionalUpdate
from app.services.errores import ProfesionalNoEncontradoError
from app.services.profesional_service import (
    actualizar,
    crear,
    desactivar,
    listar_activos,
    obtener_activo,
)


def test_listar_activos_excluye_al_inactivo_de_la_fixture(db, datos):
    activos = listar_activos(db)

    assert [profesional.id for profesional in activos] == [datos.prof_activo.id]
    assert all(profesional.activo is True for profesional in activos)
    assert datos.prof_inactivo.id not in [profesional.id for profesional in activos]


def test_obtener_activo_devuelve_el_profesional_activo(db, datos):
    profesional = obtener_activo(db, datos.prof_activo.id)

    assert profesional.id == datos.prof_activo.id
    assert profesional.nombre == "Ana"
    assert profesional.especialidad == "Ortodoncia"


def test_obtener_activo_rechaza_inactivo_e_inexistente(db, datos):
    with pytest.raises(ProfesionalNoEncontradoError) as error_inactivo:
        obtener_activo(db, datos.prof_inactivo.id)

    assert "activo" in error_inactivo.value.motivo
    assert str(datos.prof_inactivo.id) in error_inactivo.value.motivo

    with pytest.raises(ProfesionalNoEncontradoError) as error_inexistente:
        obtener_activo(db, 999999)

    assert "999999" in error_inexistente.value.motivo
    assert db.scalar(select(Profesional).where(Profesional.id == 999999)) is None

    with pytest.raises(ProfesionalNoEncontradoError):
        obtener_activo(db, 0)


def test_listar_activos_devuelve_varios_ordenados_y_respeta_baja_logica(db, datos):
    segunda = Profesional(
        nombre="Carla", apellido="Méndez", especialidad="Odontopediatría"
    )
    db.add(segunda)
    db.commit()
    db.refresh(segunda)

    activos = listar_activos(db)
    assert [profesional.id for profesional in activos] == [
        datos.prof_activo.id,
        segunda.id,
    ]

    datos.prof_activo.activo = False
    db.add(datos.prof_activo)
    db.commit()

    assert [profesional.id for profesional in listar_activos(db)] == [segunda.id]


def test_crear_persiste_el_payload_validado_y_queda_activo(db, datos):
    payload = ProfesionalCreate(
        nombre="Valeria", apellido="Sosa", especialidad="Periodoncia"
    )

    creado = crear(db, payload)

    assert creado.id is not None
    assert creado.activo is True
    assert (creado.nombre, creado.apellido, creado.especialidad) == (
        "Valeria",
        "Sosa",
        "Periodoncia",
    )
    persistido = db.get(Profesional, creado.id)
    assert persistido is creado
    assert [profesional.id for profesional in listar_activos(db)] == [
        datos.prof_activo.id,
        creado.id,
    ]


def test_crear_respeta_activo_explicito_falso_y_especialidad_ausente(db, datos):
    creado = crear(
        db,
        ProfesionalCreate(
            nombre="Nora", apellido="Flores", activo=False, especialidad=None
        ),
    )

    activa = crear(db, ProfesionalCreate(nombre="Iris", apellido="Vega"))

    assert creado.activo is False
    assert creado.especialidad is None
    assert activa.activo is True
    assert [profesional.id for profesional in listar_activos(db)] == [
        datos.prof_activo.id,
        activa.id,
    ]


def test_actualizar_edita_campos_y_desactiva_sin_borrar(db, datos):
    profesional_id = datos.prof_activo.id

    actualizado = actualizar(
        db,
        profesional_id,
        ProfesionalUpdate(especialidad="Endodoncia", activo=False),
    )

    assert actualizado.id == profesional_id
    assert actualizado.especialidad == "Endodoncia"
    assert actualizado.activo is False
    assert actualizado.nombre == "Ana"
    assert db.get(Profesional, profesional_id) is not None
    assert profesional_id not in [p.id for p in listar_activos(db)]


def test_actualizar_reactiva_y_rechaza_id_inexistente(db, datos):
    inactivo_id = datos.prof_inactivo.id

    reactivado = actualizar(db, inactivo_id, ProfesionalUpdate(activo=True))

    assert reactivado.activo is True
    assert reactivado.nombre == "Jorge"
    assert inactivo_id in [p.id for p in listar_activos(db)]
    assert obtener_activo(db, inactivo_id).id == inactivo_id

    with pytest.raises(ProfesionalNoEncontradoError) as error:
        actualizar(db, 888888, ProfesionalUpdate(nombre="Nora"))

    assert "888888" in error.value.motivo
    assert db.get(Profesional, 888888) is None


def test_actualizar_parcial_no_toca_campos_no_enviados_y_rechaza_solo_nulos(db, datos):
    actualizado = actualizar(
        db, datos.prof_activo.id, ProfesionalUpdate(nombre=" Ana María ")
    )

    assert actualizado.nombre == "Ana María"
    assert actualizado.apellido == "Rivas"
    assert actualizado.especialidad == "Ortodoncia"
    assert actualizado.activo is True

    con_apellido = actualizar(
        db, datos.prof_activo.id, ProfesionalUpdate(apellido="Rivas Sosa")
    )
    assert con_apellido.apellido == "Rivas Sosa"
    assert con_apellido.nombre == "Ana María"

    with pytest.raises(ValidationError):
        ProfesionalUpdate(especialidad=None)


def test_desactivar_con_turnos_y_usuario_preserva_el_historico(db, datos):
    inicio = datetime(2026, 11, 25, 10, 0)
    turno = Turno(
        profesional_id=datos.prof_activo.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_1.id,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=inicio + timedelta(minutes=30),
    )
    usuario = Usuario(
        email="odonto-historico@clinica.local",
        password_hash=security.hash_password("clave-ficticia-de-prueba"),
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=datos.prof_activo.id,
    )
    db.add_all([turno, usuario])
    db.commit()
    db.refresh(turno)
    db.refresh(usuario)

    bajado = desactivar(db, datos.prof_activo.id)

    assert bajado.activo is False
    assert db.get(Profesional, datos.prof_activo.id) is not None
    assert db.get(Turno, turno.id) is not None
    assert db.get(Usuario, usuario.id).profesional_id == datos.prof_activo.id
    assert datos.prof_activo.id not in [p.id for p in listar_activos(db)]


def test_desactivar_sin_turnos_tambien_es_logica_e_idempotente(db, datos):
    total_antes = db.scalar(select(func.count()).select_from(Profesional))

    bajado = desactivar(db, datos.prof_activo.id)
    assert bajado.activo is False

    segunda = desactivar(db, datos.prof_activo.id)
    assert segunda.activo is False
    assert segunda.id == bajado.id

    assert db.scalar(select(func.count()).select_from(Profesional)) == total_antes
    assert db.get(Profesional, datos.prof_activo.id) is not None

    with pytest.raises(ProfesionalNoEncontradoError) as error:
        desactivar(db, 777777)

    assert "777777" in error.value.motivo


def test_desactivar_ya_inactivo_no_duplica_y_no_toca_turnos(db, datos):
    inicio = datetime(2026, 12, 1, 9, 0)
    turnos = [
        Turno(
            profesional_id=datos.prof_activo.id,
            paciente_id=datos.paciente.id,
            prestacion_id=datos.prestacion_30.id,
            sillon_id=datos.sillon_1.id,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=inicio + timedelta(minutes=30),
        ),
        Turno(
            profesional_id=datos.prof_activo.id,
            paciente_id=datos.paciente.id,
            prestacion_id=datos.prestacion_30.id,
            sillon_id=datos.sillon_2.id,
            fecha_hora_inicio=inicio + timedelta(hours=1),
            fecha_hora_fin=inicio + timedelta(hours=1, minutes=30),
        ),
    ]
    db.add_all(turnos)
    db.commit()
    turnos_antes = db.scalar(select(func.count()).select_from(Turno))

    inactivo = desactivar(db, datos.prof_inactivo.id)
    assert inactivo.activo is False

    bajado = desactivar(db, datos.prof_activo.id)
    assert bajado.activo is False
    assert db.scalar(select(func.count()).select_from(Profesional)) == 2
    assert db.scalar(select(func.count()).select_from(Turno)) == turnos_antes == 2
