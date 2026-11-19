from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.core import security
from app.core.deps import oauth2_scheme, require_odontologo_own
from app.core.handlers import registrar_manejadores_auth
from app.db.session import get_db
from app.main import app
from app.models import Profesional, Turno, Usuario
from app.models.usuario import RolUsuario
from app.services import auth_service


def test_esquema_bearer_aparece_en_openapi_y_protege_la_ruta():
    aplicacion = FastAPI()

    @aplicacion.get("/privada")
    def privada(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
        return {"token": token}

    esquemas = aplicacion.openapi()["components"]["securitySchemes"]

    esquema = esquemas["OAuth2PasswordBearer"]

    assert esquema["type"] == "oauth2"
    assert esquema["flows"]["password"]["tokenUrl"] == "/auth/login"
    assert oauth2_scheme.model.flows.password.tokenUrl == "/auth/login"

    with TestClient(aplicacion) as client:
        assert client.get("/privada").status_code == 401


def test_login_form_urlencoded():
    aplicacion = FastAPI()

    @aplicacion.post("/auth/login")
    def login(form: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
        return {"usuario": form.username, "clave": form.password}

    with TestClient(aplicacion) as client:
        respuesta = client.post(
            "/auth/login",
            data={
                "username": "admin@clinica.local",
                "password": "clave-ficticia-de-prueba",
            },
        )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "usuario": "admin@clinica.local",
        "clave": "clave-ficticia-de-prueba",
    }


CLAVE_FICTICIA = "clave-secreta-de-prueba"


def _crear_usuario(
    db,
    *,
    email: str,
    rol: RolUsuario = RolUsuario.ADMIN,
    profesional_id: int | None = None,
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


def test_login_admin_devuelve_jwt_con_los_cuatro_claims(client, db, monkeypatch):
    monkeypatch.setattr(auth_service, "_intentos", {})
    usuario = _crear_usuario(db, email="admin-api@clinica.local")
    antes = int(datetime.now(UTC).timestamp())

    respuesta = client.post(
        "/auth/login",
        data={"username": usuario.email, "password": CLAVE_FICTICIA},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "Bearer"
    assert "password_hash" not in cuerpo

    claims = security.decode_access_token(cuerpo["access_token"])
    assert claims["sub"] == str(usuario.id)
    assert claims["rol"] == "admin"
    assert claims["profesional_id"] is None
    assert antes <= claims["exp"] <= antes + 480 * 60 + 5


def test_login_odontologo_devuelve_su_profesional_id(client, db, monkeypatch):
    monkeypatch.setattr(auth_service, "_intentos", {})
    profesional = Profesional(nombre="Ana", apellido="Rivas")
    db.add(profesional)
    db.commit()
    db.refresh(profesional)
    usuario = _crear_usuario(
        db,
        email="odonto-api@clinica.local",
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=profesional.id,
    )

    respuesta = client.post(
        "/auth/login",
        data={"username": usuario.email, "password": CLAVE_FICTICIA},
    )

    assert respuesta.status_code == 200
    claims = security.decode_access_token(respuesta.json()["access_token"])
    assert claims["rol"] == "odontologo"
    assert claims["profesional_id"] == profesional.id
    assert "password_hash" not in respuesta.json()


def test_login_contrasena_incorrecta_y_sexto_intento(client, db, monkeypatch):
    monkeypatch.setattr(auth_service, "_intentos", {})
    usuario = _crear_usuario(db, email="admin-rate@clinica.local")

    for _ in range(5):
        respuesta = client.post(
            "/auth/login",
            data={"username": usuario.email, "password": "clave-erronea"},
        )
        assert respuesta.status_code == 401
        assert "access_token" not in respuesta.json()

    respuesta = client.post(
        "/auth/login",
        data={"username": usuario.email, "password": CLAVE_FICTICIA},
    )

    assert respuesta.status_code == 429
    assert "access_token" not in respuesta.json()


def _token(usuario: Usuario, minutos: int = 5) -> str:
    return security.create_access_token(
        {
            "sub": str(usuario.id),
            "rol": str(usuario.rol),
            "profesional_id": usuario.profesional_id,
        },
        expires_delta=timedelta(minutes=minutos),
    )


def test_me_devuelve_la_identidad_sin_password_hash(client, db):
    usuario = _crear_usuario(db, email="admin-me@clinica.local")

    respuesta = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {_token(usuario)}"}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo == {
        "id": usuario.id,
        "email": usuario.email,
        "rol": "admin",
        "profesional_id": None,
    }
    assert "password_hash" not in cuerpo
    assert usuario.password_hash not in respuesta.text


def test_me_rechaza_acceso_sin_token_y_token_expirado(client, db):
    usuario = _crear_usuario(db, email="admin-me@clinica.local")

    assert client.get("/auth/me").status_code == 401

    respuesta = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {_token(usuario, minutos=-1)}"},
    )
    assert respuesta.status_code == 401
    assert "expiró" in respuesta.text


def test_admin_crea_usuario_odontologo_con_password_hasheado(client, db):
    admin = _crear_usuario(db, email="admin-crud@clinica.local")
    profesional = Profesional(nombre="Ana", apellido="Rivas")
    db.add(profesional)
    db.commit()
    db.refresh(profesional)
    email_nuevo = "nuevo-odonto@clinica.local"

    respuesta = client.post(
        "/auth/usuarios",
        json={
            "email": email_nuevo,
            "password": CLAVE_FICTICIA,
            "rol": "odontologo",
            "profesional_id": profesional.id,
        },
        headers={"Authorization": f"Bearer {_token(admin)}"},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert "password_hash" not in cuerpo
    assert cuerpo["email"] == email_nuevo
    assert cuerpo["rol"] == "odontologo"
    assert cuerpo["profesional_id"] == profesional.id

    creado = db.scalar(select(Usuario).where(Usuario.email == email_nuevo))
    assert creado is not None
    assert creado.password_hash != CLAVE_FICTICIA
    assert security.verify_password(CLAVE_FICTICIA, creado.password_hash) is True


def test_odontologo_no_puede_crear_usuarios(client, db):
    profesional = Profesional(nombre="Ana", apellido="Rivas")
    db.add(profesional)
    db.commit()
    db.refresh(profesional)
    odontologo = _crear_usuario(
        db,
        email="odonto-crud@clinica.local",
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=profesional.id,
    )
    email_nuevo = "prohibido@clinica.local"

    respuesta = client.post(
        "/auth/usuarios",
        json={
            "email": email_nuevo,
            "password": CLAVE_FICTICIA,
            "rol": "admin",
        },
        headers={"Authorization": f"Bearer {_token(odontologo)}"},
    )

    assert respuesta.status_code == 403
    assert db.scalar(select(Usuario).where(Usuario.email == email_nuevo)) is None


@pytest.fixture
def client_turnos_rbac(db):
    aplicacion = FastAPI()
    registrar_manejadores_auth(aplicacion)

    @aplicacion.get("/turnos-protegidos")
    def listar_turnos(
        profesional_id: int,
        sesion=Depends(get_db),
        _usuario: Usuario = Depends(require_odontologo_own),
    ) -> dict[str, list[int]]:
        ids = sesion.scalars(
            select(Turno.id).where(Turno.profesional_id == profesional_id)
        ).all()
        return {"ids": list(ids)}

    def _override_get_db():
        yield db

    aplicacion.dependency_overrides[get_db] = _override_get_db
    with TestClient(aplicacion) as cliente:
        yield cliente


def test_odontologo_solo_ve_sus_turnos_y_no_los_de_otro_profesional(
    client_turnos_rbac, db, datos
):
    odontologo = _crear_usuario(
        db,
        email="odonto-turnos@clinica.local",
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=datos.prof_activo.id,
    )
    otro = Profesional(nombre="Carla", apellido="Méndez")
    db.add(otro)
    db.commit()
    db.refresh(otro)

    inicio = datetime(2026, 11, 5, 9, 0, 0)
    propio = Turno(
        profesional_id=datos.prof_activo.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_1.id,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=inicio + timedelta(minutes=30),
    )
    ajeno = Turno(
        profesional_id=otro.id,
        paciente_id=datos.paciente.id,
        prestacion_id=datos.prestacion_30.id,
        sillon_id=datos.sillon_2.id,
        fecha_hora_inicio=inicio + timedelta(hours=1),
        fecha_hora_fin=inicio + timedelta(hours=1, minutes=30),
    )
    db.add_all([propio, ajeno])
    db.commit()
    db.refresh(propio)

    headers = {"Authorization": f"Bearer {_token(odontologo)}"}

    respuesta_propia = client_turnos_rbac.get(
        "/turnos-protegidos",
        params={"profesional_id": datos.prof_activo.id},
        headers=headers,
    )
    respuesta_ajena = client_turnos_rbac.get(
        "/turnos-protegidos", params={"profesional_id": otro.id}, headers=headers
    )

    assert respuesta_propia.status_code == 200
    assert respuesta_propia.json() == {"ids": [propio.id]}
    assert respuesta_ajena.status_code == 403
    assert "ids" not in respuesta_ajena.json()


def test_health_publico_y_openapi_expone_auth_sin_middleware_global(client):
    salud = client.get("/api/health")

    assert salud.status_code == 200
    assert salud.json() == {"status": "ok"}

    esquema = client.get("/openapi.json").json()
    rutas = esquema["paths"]

    assert "/auth/login" in rutas
    assert "/auth/me" in rutas
    assert not any(
        "auth" in middleware.cls.__name__.lower() for middleware in app.user_middleware
    )


DEPENDENCIAS_DE_AUTH = {
    "get_current_user",
    "oauth2_scheme",
    "require_role",
    "require_odontologo_own",
    "verificar_rol",
    "verificar_profesional_own",
    "usuario_desde_token",
}


def _dependencias(dependiente) -> Iterator[object]:
    for dependencia in dependiente.dependencies:
        yield dependencia.call
        yield from _dependencias(dependencia)


def test_rutas_publico_de_la_app_no_llevan_dependencias_de_auth(client):
    publicas = [
        ruta
        for ruta in app.routes
        if getattr(ruta, "path", "").startswith("/turnos/online")
    ]

    for ruta in publicas:
        nombres = {
            getattr(llamada, "__name__", "")
            for llamada in _dependencias(ruta.dependant)
        }
        assert not nombres & DEPENDENCIAS_DE_AUTH

    esquema = client.get("/openapi.json").json()
    for ruta in publicas:
        operaciones = esquema["paths"].get(ruta.path, {})
        assert all(not operacion.get("security") for operacion in operaciones.values())

    assert client.get("/api/health").status_code == 200


@pytest.fixture
def client_publico(db) -> Iterator[TestClient]:
    aplicacion = FastAPI()

    class ReservaPublica(BaseModel):
        model_config = ConfigDict(extra="forbid")

        email: str

    @aplicacion.get("/turnos/online/disponibles")
    def disponibles() -> dict[str, list[str]]:
        return {"franjas": ["09:00", "09:30"]}

    @aplicacion.post("/turnos/online", status_code=201)
    def reservar(payload: ReservaPublica) -> dict[str, str]:
        return {"estado": "reservado", "email": payload.email}

    @aplicacion.exception_handler(RequestValidationError)
    async def _400(_request: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": error.errors()})

    with TestClient(aplicacion) as cliente:
        yield cliente


def test_reserva_publico_no_exige_jwt_y_rechaza_estado(client_publico):
    franjas = client_publico.get("/turnos/online/disponibles")

    assert franjas.status_code == 200
    assert franjas.json() == {"franjas": ["09:00", "09:30"]}

    valida = client_publico.post(
        "/turnos/online", json={"email": "paciente-ficticio@clinica.local"}
    )
    assert valida.status_code == 201
    assert valida.json()["estado"] == "reservado"

    inyectada = client_publico.post(
        "/turnos/online",
        json={"email": "paciente-ficticio@clinica.local", "estado": "confirmado"},
    )

    assert inyectada.status_code == 400
    assert inyectada.status_code != 401
    assert inyectada.json()["detail"][0]["type"] == "extra_forbidden"


def test_login_sin_filtracion_de_clave_ni_hash_en_logs(client, db, monkeypatch, caplog):
    monkeypatch.setattr(auth_service, "_intentos", {})
    usuario = _crear_usuario(db, email="admin-logs@clinica.local")
    hash_guardado = usuario.password_hash

    fallida = client.post(
        "/auth/login",
        data={"username": usuario.email, "password": "clave-erronea-ficticia"},
    )
    valida = client.post(
        "/auth/login", data={"username": usuario.email, "password": CLAVE_FICTICIA}
    )

    assert fallida.status_code == 401
    assert valida.status_code == 200
    assert CLAVE_FICTICIA not in caplog.text
    assert "clave-erronea-ficticia" not in caplog.text
    assert hash_guardado not in caplog.text
    assert "password_hash" not in caplog.text
