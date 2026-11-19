from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core import security
from app.core.handlers import registrar_manejadores_auth
from app.db.session import get_db
from app.main import app
from app.models import Profesional, Turno, Usuario
from app.models.usuario import RolUsuario
from app.routers import profesionales


@pytest.fixture
def api(db) -> Iterator[TestClient]:
    aplicacion = FastAPI()
    registrar_manejadores_auth(aplicacion)
    aplicacion.include_router(profesionales.router)

    @aplicacion.exception_handler(RequestValidationError)
    async def _400(_request: object, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": error.errors()})

    def _override_get_db() -> Iterator[object]:
        yield db

    aplicacion.dependency_overrides[get_db] = _override_get_db
    with TestClient(aplicacion) as cliente:
        yield cliente


CLAVE_FICTICIA = "clave-ficticia-de-prueba"


def _crear_usuario(db, *, email: str, rol: RolUsuario, profesional_id=None) -> Usuario:
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
        db, email="admin-catalogo@clinica.local", rol=RolUsuario.ADMIN
    )
    return {"Authorization": f"Bearer {_token(admin)}"}


def test_listado_publico_devuelve_solo_activos_y_campos_exactos(api, datos):
    respuesta = api.get("/profesionales")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert [p["id"] for p in cuerpo] == [datos.prof_activo.id]
    profesional = cuerpo[0]
    assert set(profesional) == {
        "id",
        "nombre",
        "apellido",
        "especialidad",
        "activo",
    }
    assert profesional["nombre"] == "Ana"
    assert profesional["activo"] is True
    assert "password_hash" not in respuesta.text
    assert "Jorge" not in respuesta.text


def test_detalle_publico_de_activo_devuelve_200(api, datos):
    respuesta = api.get(f"/profesionales/{datos.prof_activo.id}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "id": datos.prof_activo.id,
        "nombre": "Ana",
        "apellido": "Rivas",
        "especialidad": "Ortodoncia",
        "activo": True,
    }


def test_detalle_publico_de_inactivo_e_inexistente_devuelve_404(api, datos):
    inactivo = api.get(f"/profesionales/{datos.prof_inactivo.id}")
    assert inactivo.status_code == 404
    assert "Jorge" not in inactivo.text
    assert "Luna" not in inactivo.text

    inexistente = api.get("/profesionales/999999")
    assert inexistente.status_code == 404


def test_listado_publico_no_filtra_pacientes_ni_credenciales(api, db, datos):
    hash_ficticio = security.hash_password("clave-ficticia-de-prueba")
    db.add(
        Usuario(
            email="odonto-privacidad@clinica.local",
            password_hash=hash_ficticio,
            rol=RolUsuario.ODONTOLOGO,
            profesional_id=datos.prof_activo.id,
        )
    )
    db.commit()

    listado = api.get("/profesionales")
    detalle = api.get(f"/profesionales/{datos.prof_activo.id}")

    for respuesta in (listado, detalle):
        assert respuesta.status_code == 200
        assert "40111222" not in respuesta.text
        assert "Lucía" not in respuesta.text
        assert "odonto-privacidad@clinica.local" not in respuesta.text
        assert hash_ficticio not in respuesta.text
        assert "password_hash" not in respuesta.text


def test_admin_crea_profesional_activo_por_defecto(api, db):
    headers = _headers_admin(db)

    respuesta = api.post(
        "/profesionales",
        json={
            "nombre": "Valeria",
            "apellido": "Sosa",
            "especialidad": "Periodoncia",
        },
        headers=headers,
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"id", "nombre", "apellido", "especialidad", "activo"}
    assert cuerpo["activo"] is True
    assert (cuerpo["nombre"], cuerpo["apellido"], cuerpo["especialidad"]) == (
        "Valeria",
        "Sosa",
        "Periodoncia",
    )
    persistido = db.get(Profesional, cuerpo["id"])
    assert persistido is not None and persistido.activo is True


def test_admin_edita_y_reactiva_un_profesional(api, db, datos):
    headers = _headers_admin(db)
    profesional_id = datos.prof_activo.id

    editado = api.put(
        f"/profesionales/{profesional_id}",
        json={"especialidad": "Endodoncia", "activo": False},
        headers=headers,
    )
    assert editado.status_code == 200
    assert editado.json()["especialidad"] == "Endodoncia"
    assert editado.json()["activo"] is False
    assert api.get(f"/profesionales/{profesional_id}").status_code == 404

    reactivado = api.put(
        f"/profesionales/{profesional_id}", json={"activo": True}, headers=headers
    )
    assert reactivado.status_code == 200
    assert reactivado.json()["activo"] is True
    assert [p["id"] for p in api.get("/profesionales").json()] == [profesional_id]

    inexistente = api.put(
        "/profesionales/999999", json={"nombre": "Nora"}, headers=headers
    )
    assert inexistente.status_code == 404
    assert db.get(Profesional, 999999) is None


def test_admin_da_de_baja_con_turnos_sin_turnos_y_de_forma_idempotente(
    api, db, datos
):
    headers = _headers_admin(db)
    inicio = datetime(2026, 12, 2, 11, 0)
    turno = Turno(
        profesional_id=datos.prof_activo.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_1.id,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=inicio + timedelta(minutes=30),
    )
    db.add(turno)
    db.commit()
    db.refresh(turno)

    baja = api.delete(f"/profesionales/{datos.prof_activo.id}", headers=headers)
    assert baja.status_code == 200
    assert baja.json()["activo"] is False
    assert db.get(Turno, turno.id) is not None
    assert db.get(Profesional, datos.prof_activo.id) is not None
    assert api.get("/profesionales").json() == []

    repeticion = api.delete(f"/profesionales/{datos.prof_activo.id}", headers=headers)
    assert repeticion.status_code == 200
    assert repeticion.json()["activo"] is False
    assert db.scalar(select(func.count()).select_from(Profesional)) == 2

    sin_turnos = api.delete(f"/profesionales/{datos.prof_inactivo.id}", headers=headers)
    assert sin_turnos.status_code == 200
    assert sin_turnos.json()["activo"] is False

    inexistente = api.delete("/profesionales/999999", headers=headers)
    assert inexistente.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"nombre": "", "apellido": "Sosa"},
        {"nombre": "Valeria", "apellido": "   "},
        {"nombre": "Valeria", "apellido": "Sosa", "activo": "si"},
        {"id": 99, "nombre": "Valeria", "apellido": "Sosa"},
        {"nombre": "Valeria", "apellido": "Sosa", "estado": "reservado"},
    ],
)
def test_admin_alta_rechaza_payloads_invalidos(api, db, payload):
    headers = _headers_admin(db)
    total_antes = db.scalar(select(func.count()).select_from(Profesional))

    respuesta = api.post("/profesionales", json=payload, headers=headers)

    assert respuesta.status_code == 400
    assert db.scalar(select(func.count()).select_from(Profesional)) == total_antes


@pytest.mark.parametrize(
    ("payload", "campo"),
    [
        ({"nombre": "", "apellido": "Sosa"}, "nombre"),
        ({"nombre": "Valeria", "apellido": "   "}, "apellido"),
    ],
)
def test_admin_alta_rechaza_vacio_indicando_el_campo(api, db, payload, campo):
    headers = _headers_admin(db)

    respuesta = api.post("/profesionales", json=payload, headers=headers)

    assert respuesta.status_code == 400
    assert campo in respuesta.json()["detail"][0]["loc"]


@pytest.mark.parametrize("payload", [{}, {"activo": "si"}, {"id": 9}])
def test_admin_edicion_rechaza_cuerpo_invalido(api, db, datos, payload):
    headers = _headers_admin(db)
    antes = (datos.prof_activo.nombre, datos.prof_activo.especialidad)

    respuesta = api.put(
        f"/profesionales/{datos.prof_activo.id}", json=payload, headers=headers
    )

    assert respuesta.status_code == 400
    assert (datos.prof_activo.nombre, datos.prof_activo.especialidad) == antes


def test_app_registra_las_cinco_rutas_y_mantiene_health(client):
    esquema = app.openapi()
    rutas = esquema["paths"]

    assert "/profesionales" in rutas
    assert "/profesionales/{profesional_id}" in rutas
    operaciones = {
        **rutas["/profesionales"],
        **rutas["/profesionales/{profesional_id}"],
    }
    assert set(operaciones) == {"get", "post", "put", "delete"}

    assert "/auth/login" in rutas
    assert "/auth/me" in rutas
    assert "/turnos" in rutas

    respuesta = client.get("/api/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}
    assert client.get("/profesionales").status_code == 200


def test_app_real_devuelve_400_serializable_para_cuerpo_vacio(client, db, datos):
    respuesta = client.put(
        f"/profesionales/{datos.prof_activo.id}",
        json={},
        headers=_headers_admin(db),
    )

    assert respuesta.status_code == 400
    assert "al menos un campo" in respuesta.text
    assert db.get(Profesional, datos.prof_activo.id).nombre == "Ana"


def test_sin_token_las_tres_rutas_de_admin_devuelven_401_sin_mutar(client, db, datos):
    total_antes = db.scalar(select(func.count()).select_from(Profesional))
    nombre_antes = datos.prof_activo.nombre
    payload = {"nombre": "Inyectado", "apellido": "Sin Token"}

    alta = client.post("/profesionales", json=payload)
    edicion = client.put(f"/profesionales/{datos.prof_activo.id}", json=payload)
    baja = client.delete(f"/profesionales/{datos.prof_activo.id}")

    assert [alta.status_code, edicion.status_code, baja.status_code] == [401, 401, 401]
    assert db.scalar(select(func.count()).select_from(Profesional)) == total_antes
    assert db.get(Profesional, datos.prof_activo.id).nombre == nombre_antes

    for header in ({"Authorization": "Bearer"}, {"Authorization": "Token inventado"}):
        respuesta = client.delete(
            f"/profesionales/{datos.prof_activo.id}", headers=header
        )
        assert respuesta.status_code == 401

    assert db.get(Profesional, datos.prof_activo.id).nombre == nombre_antes


def test_token_vencido_y_firma_invalida_devuelven_401(client, db, datos):
    total_antes = db.scalar(select(func.count()).select_from(Profesional))
    admin = _crear_usuario(db, email="admin-token@clinica.local", rol=RolUsuario.ADMIN)
    vencido = _token(admin, minutos=-1)
    firma_ajena = jwt.encode(
        {
            "sub": str(admin.id),
            "rol": "admin",
            "profesional_id": None,
            "exp": datetime.now(UTC) + timedelta(hours=1),
        },
        "clave-ficticia-distinta-para-firmar-token",
        algorithm="HS256",
    )

    respuesta_vencida = client.delete(
        f"/profesionales/{datos.prof_inactivo.id}",
        headers={"Authorization": f"Bearer {vencido}"},
    )
    respuesta_firma = client.post(
        "/profesionales",
        json={"nombre": "Inyectado", "apellido": "Firma Ajena"},
        headers={"Authorization": f"Bearer {firma_ajena}"},
    )

    assert respuesta_vencida.status_code == 401
    assert "expiró" in respuesta_vencida.text
    assert respuesta_firma.status_code == 401
    assert db.scalar(select(func.count()).select_from(Profesional)) == total_antes
    assert "Inyectado" not in [p.nombre for p in db.scalars(select(Profesional))]


def test_odontologo_no_puede_administrar_catalogo_y_no_hay_cambios(client, db, datos):
    odontologo = _crear_usuario(
        db,
        email="odonto-catalogo@clinica.local",
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=datos.prof_activo.id,
    )
    headers = {"Authorization": f"Bearer {_token(odontologo)}"}
    total_antes = db.scalar(select(func.count()).select_from(Profesional))
    nombre_antes = datos.prof_activo.nombre
    activo_antes = datos.prof_activo.activo
    payload = {"nombre": "Inyectado", "apellido": "Por Odonto"}

    alta = client.post("/profesionales", json=payload, headers=headers)
    edicion = client.put(
        f"/profesionales/{datos.prof_activo.id}", json=payload, headers=headers
    )
    baja = client.delete(f"/profesionales/{datos.prof_activo.id}", headers=headers)

    assert [alta.status_code, edicion.status_code, baja.status_code] == [403, 403, 403]
    assert db.scalar(select(func.count()).select_from(Profesional)) == total_antes
    assert db.get(Profesional, datos.prof_activo.id).nombre == nombre_antes
    assert db.get(Profesional, datos.prof_activo.id).activo == activo_antes
    assert "Inyectado" not in [p.nombre for p in db.scalars(select(Profesional))]
    assert "permiso" in alta.text
    assert client.get("/profesionales").status_code == 200
    assert client.get(f"/profesionales/{datos.prof_activo.id}").status_code == 200


def test_catalogo_no_filtra_claves_ni_datos_de_terceros_en_respuesta_ni_logs(
    client, db, datos, caplog
):
    admin = _crear_usuario(
        db, email="admin-privacidad@clinica.local", rol=RolUsuario.ADMIN
    )
    hash_admin = admin.password_hash
    inicio = datetime(2026, 12, 3, 8, 0)
    db.add(
        Turno(
            profesional_id=datos.prof_activo.id,
            paciente_id=datos.paciente.id,
            prestacion_id=datos.prestacion_30.id,
            sillon_id=datos.sillon_1.id,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=inicio + timedelta(minutes=30),
        )
    )
    db.commit()
    headers = {"Authorization": f"Bearer {_token(admin)}"}

    with caplog.at_level("DEBUG"):
        respuestas = [
            client.get("/profesionales"),
            client.get(f"/profesionales/{datos.prof_activo.id}"),
            client.post(
                "/profesionales",
                json={"nombre": "Nora", "apellido": "Flores"},
                headers=headers,
            ),
            client.put(
                f"/profesionales/{datos.prof_activo.id}",
                json={"especialidad": "Endodoncia"},
                headers=headers,
            ),
            client.delete(f"/profesionales/{datos.prof_inactivo.id}", headers=headers),
        ]

    secretos = [
        hash_admin,
        CLAVE_FICTICIA,
        "password_hash",
        "40111222",
        "Lucía",
        "33444555",
        "Sofía",
    ]
    for respuesta in respuestas:
        assert respuesta.status_code in (200, 201)
        for secreto in secretos:
            assert secreto not in respuesta.text
    for secreto in secretos:
        assert secreto not in caplog.text

    no_encontrado = client.get("/profesionales/999999")
    assert no_encontrado.status_code == 404
    for secreto in secretos:
        assert secreto not in no_encontrado.text
