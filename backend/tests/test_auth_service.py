from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt as pyjwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core import security
from app.core.deps import get_current_user, require_odontologo_own, require_role
from app.core.handlers import registrar_manejadores_auth
from app.db.session import get_db
from app.models import Profesional, Usuario
from app.models.usuario import RolUsuario
from app.services import auth_service
from app.services.errores import (
    CredencialesInvalidasError,
    IntentosExcedidosError,
    TokenExpiradoError,
    TokenInvalidoError,
)


def test_token_claims_y_expiracion():
    antes = int(datetime.now(UTC).timestamp())

    token = security.create_access_token(
        {"sub": "5", "rol": "odontologo", "profesional_id": 8}
    )
    claims = security.decode_access_token(token)

    assert claims["sub"] == "5"
    assert claims["rol"] == "odontologo"
    assert claims["profesional_id"] == 8
    assert antes <= claims["exp"] <= antes + 480 * 60 + 5


def test_token_expirado_y_token_con_firma_ajena_se_rechazan():
    vencido = security.create_access_token(
        {"sub": "5", "rol": "admin", "profesional_id": None},
        expires_delta=timedelta(minutes=-1),
    )
    with pytest.raises(TokenExpiradoError, match="expiró"):
        security.decode_access_token(vencido)

    clave_ajena = "clave-ajena-ficticia-con-longitud-suficiente-para-hs256"
    expiracion = datetime.now(UTC) + timedelta(minutes=5)
    ajeno = pyjwt.encode(
        {"sub": "5", "exp": expiracion}, clave_ajena, algorithm="HS256"
    )
    with pytest.raises(TokenInvalidoError):
        security.decode_access_token(ajeno)


HASH_PBKDF2_LEGADO = (
    "pbkdf2_sha256$240000$fb55c920cc41d55f36b977f74b24f373$"
    "6c854f4895fb60062f9c4b6c6ef2da468397ae1cbdc13c7649dfdf72032f16e2"
)
CLAVE_FICTICIA = "clave-secreta-de-prueba"


def _crear_usuario(
    db,
    *,
    email: str,
    password_hash: str,
    activo: bool = True,
    rol: RolUsuario = RolUsuario.ADMIN,
    profesional_id: int | None = None,
) -> Usuario:
    usuario = Usuario(
        email=email,
        password_hash=password_hash,
        rol=rol,
        profesional_id=profesional_id,
        activo=activo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def test_credenciales_contrasena_incorrecta_son_rechazadas(db):
    _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )

    with pytest.raises(CredencialesInvalidasError) as error:
        auth_service.autenticar(db, "admin@clinica.local", "clave-erronea")

    assert str(error.value) == "Usuario o contraseña incorrectos."


def test_credenciales_usuario_inexistente_dan_el_mismo_error(db):
    _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )

    with pytest.raises(CredencialesInvalidasError) as error:
        auth_service.autenticar(db, "no-existe@clinica.local", CLAVE_FICTICIA)

    assert str(error.value) == "Usuario o contraseña incorrectos."


def test_credenciales_correctas_devuelven_usuario_y_rehashean_el_legado(db):
    usuario = _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=HASH_PBKDF2_LEGADO,
    )
    hash_inicial = usuario.password_hash

    autenticado = auth_service.autenticar(db, "admin@clinica.local", CLAVE_FICTICIA)

    assert autenticado.id == usuario.id
    assert autenticado.password_hash.startswith("$2b$")
    assert autenticado.password_hash != hash_inicial
    assert security.verify_password(CLAVE_FICTICIA, autenticado.password_hash) is True


@pytest.fixture
def client_usuario_actual(db: Session):
    aplicacion = FastAPI()
    registrar_manejadores_auth(aplicacion)

    @aplicacion.get("/privada")
    def privada(usuario: Usuario = Depends(get_current_user)) -> dict[str, object]:
        return {"id": usuario.id, "email": usuario.email}

    def _override_get_db():
        yield db

    aplicacion.dependency_overrides[get_db] = _override_get_db
    with TestClient(aplicacion) as cliente:
        yield cliente


def _token_para(usuario: Usuario, minutos: int = 5) -> str:
    return security.create_access_token(
        {
            "sub": str(usuario.id),
            "rol": str(usuario.rol),
            "profesional_id": usuario.profesional_id,
        },
        expires_delta=timedelta(minutes=minutos),
    )


def test_usuario_actual_se_resuelve_desde_la_db_en_cada_request(
    client_usuario_actual, db
):
    usuario = _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )

    respuesta = client_usuario_actual.get(
        "/privada", headers={"Authorization": f"Bearer {_token_para(usuario)}"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": usuario.id, "email": usuario.email}


def test_usuario_actual_rechaza_acceso_sin_token_y_token_expirado(
    client_usuario_actual, db
):
    usuario = _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )

    assert client_usuario_actual.get("/privada").status_code == 401

    vencido = _token_para(usuario, minutos=-1)
    respuesta = client_usuario_actual.get(
        "/privada", headers={"Authorization": f"Bearer {vencido}"}
    )
    assert respuesta.status_code == 401


def test_usuario_actual_rechaza_usuario_inactivo_y_usuario_inexistente(
    client_usuario_actual, db
):
    inactivo = _crear_usuario(
        db,
        email="inactivo@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
        activo=False,
    )

    respuesta = client_usuario_actual.get(
        "/privada", headers={"Authorization": f"Bearer {_token_para(inactivo)}"}
    )
    assert respuesta.status_code == 401

    token_huerfano = security.create_access_token(
        {"sub": "9999", "rol": "admin"}, expires_delta=timedelta(minutes=5)
    )
    respuesta = client_usuario_actual.get(
        "/privada", headers={"Authorization": f"Bearer {token_huerfano}"}
    )
    assert respuesta.status_code == 401


@pytest.fixture
def client_rbac(db: Session):
    aplicacion = FastAPI()
    registrar_manejadores_auth(aplicacion)

    @aplicacion.get("/solo-admin")
    def solo_admin(
        usuario: Usuario = Depends(require_role(RolUsuario.ADMIN)),
    ) -> dict[str, object]:
        return {"id": usuario.id}

    @aplicacion.get("/turnos-protegidos")
    def turnos_protegidos(
        profesional_id: int,
        usuario: Usuario = Depends(require_odontologo_own),
    ) -> dict[str, object]:
        return {"id": usuario.id, "profesional_id": profesional_id}

    def _override_get_db():
        yield db

    aplicacion.dependency_overrides[get_db] = _override_get_db
    with TestClient(aplicacion) as cliente:
        yield cliente


def _headers(usuario: Usuario) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token_para(usuario)}"}


def test_rbac_admin_permitido_y_odontologo_rechazado_para_usuarios(client_rbac, db):
    admin = _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )
    odontologo = _crear_usuario(
        db,
        email="odonto@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
        rol=RolUsuario.ODONTOLOGO,
    )

    permitido = client_rbac.get("/solo-admin", headers=_headers(admin))
    rechazado = client_rbac.get("/solo-admin", headers=_headers(odontologo))

    assert permitido.status_code == 200
    assert permitido.json() == {"id": admin.id}
    assert rechazado.status_code == 403


def test_rbac_odontologo_solo_consulta_su_profesional_id(client_rbac, db):
    profesional = Profesional(nombre="Ana", apellido="Rivas")
    db.add(profesional)
    db.commit()
    db.refresh(profesional)

    odontologo = _crear_usuario(
        db,
        email="odonto@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=profesional.id,
    )

    propio = client_rbac.get(
        "/turnos-protegidos",
        params={"profesional_id": profesional.id},
        headers=_headers(odontologo),
    )
    ajeno = client_rbac.get(
        "/turnos-protegidos",
        params={"profesional_id": profesional.id + 99},
        headers=_headers(odontologo),
    )

    assert propio.status_code == 200
    assert propio.json() == {"id": odontologo.id, "profesional_id": profesional.id}
    assert ajeno.status_code == 403


def test_rbac_admin_puede_consultar_cualquier_profesional_id(client_rbac, db):
    admin = _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )

    respuesta = client_rbac.get(
        "/turnos-protegidos",
        params={"profesional_id": 999},
        headers=_headers(admin),
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": admin.id, "profesional_id": 999}


IP_FICTICIA = "203.0.113.7"


def test_rate_limit_sexto_intento_correcto_es_rechazado(db, monkeypatch):
    monkeypatch.setattr(auth_service, "_intentos", {})
    usuario = _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )

    for _ in range(5):
        with pytest.raises(CredencialesInvalidasError):
            auth_service.autenticar(db, usuario.email, "clave-erronea", ip=IP_FICTICIA)

    with pytest.raises(IntentosExcedidosError) as error:
        auth_service.autenticar(db, usuario.email, CLAVE_FICTICIA, ip=IP_FICTICIA)

    assert str(error.value) == "Demasiados intentos fallidos. Probá de nuevo más tarde."


def test_rate_limit_exito_limpia_contador_y_claves_independientes(db, monkeypatch):
    monkeypatch.setattr(auth_service, "_intentos", {})
    usuario = _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )

    for _ in range(4):
        with pytest.raises(CredencialesInvalidasError):
            auth_service.autenticar(db, usuario.email, "clave-erronea", ip=IP_FICTICIA)

    autenticado = auth_service.autenticar(
        db, usuario.email, CLAVE_FICTICIA, ip=IP_FICTICIA
    )
    assert autenticado.id == usuario.id

    for ip in (IP_FICTICIA, "203.0.113.8"):
        with pytest.raises(CredencialesInvalidasError):
            auth_service.autenticar(db, usuario.email, "clave-erronea", ip=ip)

    for _ in range(3):
        with pytest.raises(CredencialesInvalidasError):
            auth_service.autenticar(db, usuario.email, "clave-erronea", ip=IP_FICTICIA)

    assert (
        auth_service.autenticar(db, usuario.email, CLAVE_FICTICIA, ip=IP_FICTICIA).id
        == usuario.id
    )
    with pytest.raises(CredencialesInvalidasError):
        auth_service.autenticar(
            db, usuario.email, "clave-erronea", ip="203.0.113.8"
        )


def test_rate_limit_la_ventana_se_reinicia_despues_de_60_segundos(db, monkeypatch):
    monkeypatch.setattr(auth_service, "_intentos", {})
    ahora = [1000.0]
    monkeypatch.setattr(
        auth_service, "time", SimpleNamespace(monotonic=lambda: ahora[0])
    )
    usuario = _crear_usuario(
        db,
        email="admin@clinica.local",
        password_hash=security.hash_password(CLAVE_FICTICIA),
    )

    for _ in range(5):
        with pytest.raises(CredencialesInvalidasError):
            auth_service.autenticar(db, usuario.email, "clave-erronea", ip=IP_FICTICIA)

    ahora[0] += 61

    assert (
        auth_service.autenticar(db, usuario.email, CLAVE_FICTICIA, ip=IP_FICTICIA).id
        == usuario.id
    )
