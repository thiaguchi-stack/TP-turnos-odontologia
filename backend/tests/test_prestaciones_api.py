from collections.abc import Iterator
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select

from app.core import security
from app.core.handlers import registrar_manejadores_auth
from app.db.session import get_db
from app.main import app
from app.models import Prestacion, Turno, Usuario
from app.models.usuario import RolUsuario
from app.routers import prestaciones, turnos

CLAVE_FICTICIA = "clave-ficticia-de-prueba"


@pytest.fixture(autouse=True)
def reloj_fijo() -> Iterator[None]:
    with patch("app.core.clock.now", return_value=datetime(2026, 11, 4, 8, 0, 0)):
        yield


@pytest.fixture
def api(db) -> Iterator[TestClient]:
    aplicacion = FastAPI()
    registrar_manejadores_auth(aplicacion)
    aplicacion.include_router(prestaciones.router)
    aplicacion.include_router(turnos.router)

    @aplicacion.exception_handler(RequestValidationError)
    async def _400(_request: object, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": error.errors()})

    def _override_get_db() -> Iterator[object]:
        yield db

    aplicacion.dependency_overrides[get_db] = _override_get_db
    with TestClient(aplicacion) as cliente:
        yield cliente


def _crear_usuario(
    db, *, email: str, rol: RolUsuario, profesional_id: int | None = None
) -> Usuario:
    usuario = Usuario(
        email=email,
        password_hash=security.hash_password(CLAVE_FICTICIA),
        rol=rol,
        profesional_id=profesional_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _token(usuario: Usuario, minutos: int = 5) -> str:
    return security.create_access_token(
        {
            "sub": str(usuario.id),
            "rol": str(usuario.rol),
            "profesional_id": usuario.profesional_id,
        },
        expires_delta=timedelta(minutes=minutos),
    )


def _headers_admin(db) -> dict[str, str]:
    admin = _crear_usuario(
        db, email="admin-prestaciones@clinica.local", rol=RolUsuario.ADMIN
    )
    return {"Authorization": f"Bearer {_token(admin)}"}


def _headers_odontologo(db, datos) -> dict[str, str]:
    odontologo = _crear_usuario(
        db,
        email="odonto-prestaciones@clinica.local",
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=datos.prof_activo.id,
    )
    return {"Authorization": f"Bearer {_token(odontologo)}"}


def _payload_turno(datos, *, inicio: str = "2026-11-05T09:00:00", **extra):
    payload = {
        "profesional_id": datos.prof_activo.id,
        "paciente_id": datos.paciente.id,
        "prestacion_id": datos.prestacion_30.id,
        "sillon_id": datos.sillon_1.id,
        "fecha_hora_inicio": inicio,
    }
    payload.update(extra)
    return payload


def test_listado_publico_sin_token_devuelve_solo_activas(api, datos):
    respuesta = api.get("/prestaciones")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert [item["id"] for item in cuerpo] == [
        datos.prestacion_30.id,
        datos.prestacion_45.id,
    ]
    assert "Extracción" not in respuesta.text


def test_listado_publico_no_expone_campos_ajenos_al_catalogo(api, datos):
    respuesta = api.get("/prestaciones")

    assert respuesta.status_code == 200
    for item in respuesta.json():
        assert set(item) == {"id", "nombre", "duracion_minutos", "activa"}
        assert item["activa"] is True
    for secreto in ("password_hash", "40111222", "Lucía", "clínica"):
        assert secreto not in respuesta.text


def test_admin_crea_prestacion_valida(api, db):
    respuesta = api.post(
        "/prestaciones",
        json={"nombre": "Limpieza", "duracion_minutos": 30},
        headers=_headers_admin(db),
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"id", "nombre", "duracion_minutos", "activa"}
    assert (cuerpo["nombre"], cuerpo["duracion_minutos"], cuerpo["activa"]) == (
        "Limpieza",
        30,
        True,
    )
    persistida = db.get(Prestacion, cuerpo["id"])
    assert persistida is not None
    assert (persistida.nombre, persistida.duracion_minutos, persistida.activa) == (
        "Limpieza",
        30,
        True,
    )
    assert "40111222" not in respuesta.text
    assert "password_hash" not in respuesta.text


def test_alta_sin_token_401(api, db):
    total_antes = db.scalar(select(func.count()).select_from(Prestacion))

    respuesta = api.post(
        "/prestaciones", json={"nombre": "Sin token", "duracion_minutos": 30}
    )

    assert respuesta.status_code == 401
    assert db.scalar(select(func.count()).select_from(Prestacion)) == total_antes


def test_odontologo_no_puede_crear_403(api, db, datos):
    headers = _headers_odontologo(db, datos)
    total_antes = db.scalar(select(func.count()).select_from(Prestacion))

    respuesta = api.post(
        "/prestaciones",
        json={"nombre": "Inyectada", "duracion_minutos": 30},
        headers=headers,
    )

    assert respuesta.status_code == 403
    assert "permiso" in respuesta.text.lower()
    assert db.scalar(select(func.count()).select_from(Prestacion)) == total_antes
    assert "Inyectada" not in [p.nombre for p in db.scalars(select(Prestacion))]


def test_alta_duracion_cero_400(api, db):
    total_antes = db.scalar(select(func.count()).select_from(Prestacion))

    respuesta = api.post(
        "/prestaciones",
        json={"nombre": "Inválida", "duracion_minutos": 0},
        headers=_headers_admin(db),
    )

    assert respuesta.status_code == 400
    assert "mayor que cero" in respuesta.text
    assert db.scalar(select(func.count()).select_from(Prestacion)) == total_antes


def test_alta_duracion_negativa_400(api, db):
    total_antes = db.scalar(select(func.count()).select_from(Prestacion))

    respuesta = api.post(
        "/prestaciones",
        json={"nombre": "Inválida", "duracion_minutos": -5},
        headers=_headers_admin(db),
    )

    assert respuesta.status_code == 400
    assert "mayor que cero" in respuesta.text
    assert db.scalar(select(func.count()).select_from(Prestacion)) == total_antes


def test_alta_campo_extra_400(api, db):
    total_antes = db.scalar(select(func.count()).select_from(Prestacion))

    respuesta = api.post(
        "/prestaciones",
        json={
            "nombre": "Inyectada",
            "duracion_minutos": 30,
            "estado": "activa",
        },
        headers=_headers_admin(db),
    )

    assert respuesta.status_code == 400
    assert db.scalar(select(func.count()).select_from(Prestacion)) == total_antes


def test_admin_edita_nombre_y_duracion(api, db, datos):
    respuesta = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"nombre": "Limpieza profunda", "duracion_minutos": 45},
        headers=_headers_admin(db),
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"id", "nombre", "duracion_minutos", "activa"}
    assert (cuerpo["nombre"], cuerpo["duracion_minutos"], cuerpo["activa"]) == (
        "Limpieza profunda",
        45,
        True,
    )
    db.expire_all()
    persistida = db.get(Prestacion, datos.prestacion_30.id)
    assert (persistida.nombre, persistida.duracion_minutos) == (
        "Limpieza profunda",
        45,
    )


def test_edicion_sin_token_401(api, db, datos):
    respuesta = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"nombre": "Inyectada", "duracion_minutos": 90},
    )

    assert respuesta.status_code == 401
    db.expire_all()
    assert db.get(Prestacion, datos.prestacion_30.id).nombre == "Limpieza"
    assert db.get(Prestacion, datos.prestacion_30.id).duracion_minutos == 30


def test_odontologo_no_puede_editar_403(api, db, datos):
    respuesta = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"nombre": "Inyectada", "duracion_minutos": 90},
        headers=_headers_odontologo(db, datos),
    )

    assert respuesta.status_code == 403
    assert "permiso" in respuesta.text.lower()
    db.expire_all()
    persistida = db.get(Prestacion, datos.prestacion_30.id)
    assert (persistida.nombre, persistida.duracion_minutos) == ("Limpieza", 30)


def test_edicion_id_inexistente_404(api, db):
    total_antes = db.scalar(select(func.count()).select_from(Prestacion))

    respuesta = api.put(
        "/prestaciones/999999",
        json={"nombre": "Nora", "duracion_minutos": 30},
        headers=_headers_admin(db),
    )

    assert respuesta.status_code == 404
    assert db.scalar(select(func.count()).select_from(Prestacion)) == total_antes


def _editar_duracion_invalida(api, db, datos, duracion):
    respuesta = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"duracion_minutos": duracion},
        headers=_headers_admin(db),
    )

    assert respuesta.status_code == 400
    assert "mayor que cero" in respuesta.text
    db.expire_all()
    assert db.get(Prestacion, datos.prestacion_30.id).duracion_minutos == 30


def test_edicion_duracion_cero_400(api, db, datos):
    _editar_duracion_invalida(api, db, datos, 0)


def test_edicion_duracion_negativa_400(api, db, datos):
    _editar_duracion_invalida(api, db, datos, -5)


def test_openapi_y_health_publico(client, datos):
    esquema = app.openapi()
    rutas = esquema["paths"]

    assert "/prestaciones" in rutas
    assert "/prestaciones/{id}" in rutas
    operaciones = {**rutas["/prestaciones"], **rutas["/prestaciones/{id}"]}
    assert set(operaciones) == {"get", "post", "put"}
    bearer = esquema["components"]["securitySchemes"]["OAuth2PasswordBearer"]
    assert bearer["flows"]["password"]["tokenUrl"] == "/auth/login"
    assert not rutas["/prestaciones"]["get"].get("security")
    assert rutas["/prestaciones"]["post"]["security"]
    assert rutas["/prestaciones/{id}"]["put"]["security"]

    assert "/profesionales" in rutas
    assert "/turnos" in rutas
    salud = client.get("/api/health")
    assert salud.status_code == 200
    assert salud.json() == {"status": "ok"}
    assert client.get("/prestaciones").status_code == 200


def test_baja_con_turno_historico_conserva_fin(api, db, datos):
    creado = api.post("/turnos", json=_payload_turno(datos))
    assert creado.status_code == 201
    assert creado.json()["fecha_hora_fin"] == "2026-11-05T09:30:00"
    turno_id = creado.json()["id"]

    baja = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"activa": False},
        headers=_headers_admin(db),
    )

    assert baja.status_code == 200
    assert baja.json()["activa"] is False
    db.expire_all()
    persistido = db.get(Turno, turno_id)
    assert persistido is not None
    assert persistido.fecha_hora_fin == datetime(2026, 11, 5, 9, 30)
    assert persistido.prestacion_id == datos.prestacion_30.id
    assert datos.prestacion_30.id not in [
        item["id"] for item in api.get("/prestaciones").json()
    ]


def test_prestacion_inactiva_rechaza_nuevo_turno(api, db, datos):
    baja = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"activa": False},
        headers=_headers_admin(db),
    )
    assert baja.status_code == 200
    total_antes = db.scalar(select(func.count()).select_from(Turno))

    respuestas = [
        api.post("/turnos", json=_payload_turno(datos, inicio=inicio))
        for inicio in ("2026-11-05T09:00:00", "2026-11-05T11:00:00")
    ]

    for respuesta in respuestas:
        assert respuesta.status_code == 400
        assert "inactiva" in respuesta.json()["detail"].lower()
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Turno)) == total_antes


def test_reactivacion_vuelve_al_listado_publico(api, db, datos):
    headers = _headers_admin(db)
    baja = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"activa": False},
        headers=headers,
    )
    assert baja.status_code == 200
    assert datos.prestacion_30.id not in [
        item["id"] for item in api.get("/prestaciones").json()
    ]

    reactivacion = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"activa": True},
        headers=headers,
    )

    assert reactivacion.status_code == 200
    assert reactivacion.json()["activa"] is True
    listado = api.get("/prestaciones").json()
    assert datos.prestacion_30.id in [item["id"] for item in listado]
    assert next(
        item for item in listado if item["id"] == datos.prestacion_30.id
    )["activa"] is True


def test_cambio_duracion_no_modifica_turno_existente(api, db, datos):
    creado = api.post("/turnos", json=_payload_turno(datos))
    assert creado.status_code == 201
    assert creado.json()["fecha_hora_fin"] == "2026-11-05T09:30:00"
    turno_id = creado.json()["id"]
    actualizaciones_turno: list[str] = []

    def _registrar_update(
        _connection, _cursor, statement, _parameters, _context, _executemany
    ) -> None:
        if statement.lstrip().upper().startswith("UPDATE TURNO"):
            actualizaciones_turno.append(statement)

    motor = db.get_bind()
    event.listen(motor, "before_cursor_execute", _registrar_update)
    try:
        cambio = api.put(
            f"/prestaciones/{datos.prestacion_30.id}",
            json={"duracion_minutos": 60},
            headers=_headers_admin(db),
        )
    finally:
        event.remove(motor, "before_cursor_execute", _registrar_update)

    assert cambio.status_code == 200
    assert actualizaciones_turno == []
    db.expire_all()
    persistido = db.get(Turno, turno_id)
    assert persistido is not None
    assert persistido.fecha_hora_fin == datetime(2026, 11, 5, 9, 30)
    assert db.get(Prestacion, datos.prestacion_30.id).duracion_minutos == 60


def test_turno_nuevo_usa_duracion_actualizada(api, db, datos):
    cambio = api.put(
        f"/prestaciones/{datos.prestacion_30.id}",
        json={"duracion_minutos": 60},
        headers=_headers_admin(db),
    )
    assert cambio.status_code == 200

    creado = api.post("/turnos", json=_payload_turno(datos))

    assert creado.status_code == 201
    assert creado.json()["fecha_hora_inicio"] == "2026-11-05T09:00:00"
    assert creado.json()["fecha_hora_fin"] == "2026-11-05T10:00:00"

    rechazado = api.post(
        "/turnos",
        json=_payload_turno(
            datos, inicio="2026-11-05T11:00:00", duracion_minutos=15
        ),
    )
    assert rechazado.status_code == 400
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Turno)) == 1
