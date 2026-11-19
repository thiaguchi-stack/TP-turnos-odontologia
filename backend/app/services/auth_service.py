"""Servicio de autenticación: decisión de negocio, sin dependencias HTTP."""

import threading
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import security
from app.models import Profesional, Usuario
from app.models.usuario import RolUsuario
from app.schemas.auth import TokenRead, UsuarioCreate
from app.services.errores import (
    AccesoDenegadoError,
    CredencialesInvalidasError,
    IntentosExcedidosError,
    TokenInvalidoError,
    UsuarioRechazadoError,
)

_VENTANA_SEGUNDOS = 60
_MAXIMO_INTENTOS = 5
_intentos: dict[tuple[str, str], list[float]] = {}
_bloqueo_intentos = threading.Lock()


def _verificar_limite(clave: tuple[str, str], ahora: float) -> None:
    with _bloqueo_intentos:
        recientes = [
            momento
            for momento in _intentos.get(clave, ())
            if ahora - momento < _VENTANA_SEGUNDOS
        ]
        if recientes:
            _intentos[clave] = recientes
        else:
            _intentos.pop(clave, None)
        if len(recientes) >= _MAXIMO_INTENTOS:
            raise IntentosExcedidosError()


def _registrar_fallo(clave: tuple[str, str], ahora: float) -> None:
    with _bloqueo_intentos:
        _intentos.setdefault(clave, []).append(ahora)


def _limpiar_intentos(clave: tuple[str, str]) -> None:
    with _bloqueo_intentos:
        _intentos.pop(clave, None)


def autenticar(
    db: Session, email: str, password: str, ip: str = "local"
) -> Usuario:
    """Devuelve el usuario autenticado o falla con un error genérico.

    El error es idéntico para usuario inexistente, usuario inactivo y
    contraseña incorrecta (RN-AU-01/RN-AU-04). Si el hash era el legado de
    C-02 y la contraseña es correcta, se rehashea con bcrypt en este momento.
    El límite de 5 fallos por 60 s por IP+email se aplica antes de verificar.
    """
    clave = (ip, email.casefold())
    ahora = time.monotonic()
    _verificar_limite(clave, ahora)

    usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None or not usuario.activo:
        _registrar_fallo(clave, ahora)
        raise CredencialesInvalidasError()

    valido, actualizado = security.verify_and_update(
        password, usuario.password_hash
    )
    if not valido:
        _registrar_fallo(clave, ahora)
        raise CredencialesInvalidasError()

    _limpiar_intentos(clave)

    if actualizado is not None:
        usuario.password_hash = actualizado
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    return usuario


def usuario_desde_token(db: Session, token: str) -> Usuario:
    """Resuelve el usuario del token en la DB; nunca confía solo en los claims."""
    claims = security.decode_access_token(token)
    sub = claims.get("sub")

    if not isinstance(sub, str) or not sub.isdigit():
        raise TokenInvalidoError()

    usuario = db.get(Usuario, int(sub))
    if usuario is None or not usuario.activo:
        raise TokenInvalidoError("El usuario no existe o está inactivo.")

    return usuario


def emitir_token(usuario: Usuario) -> TokenRead:
    """Arma el token del usuario autenticado con los claims de identidad."""
    return TokenRead(
        access_token=security.create_access_token(
            {
                "sub": str(usuario.id),
                "rol": str(usuario.rol),
                "profesional_id": usuario.profesional_id,
            }
        )
    )


def crear_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    """Crea un usuario del sistema con contraseña hasheada (RN-AU-03/04)."""
    if db.scalar(select(Usuario).where(Usuario.email == datos.email)) is not None:
        raise UsuarioRechazadoError("Ya existe un usuario con ese email.")

    if datos.rol is RolUsuario.ODONTOLOGO:
        profesional = (
            None
            if datos.profesional_id is None
            else db.get(Profesional, datos.profesional_id)
        )
        if profesional is None:
            raise UsuarioRechazadoError(
                "El odontólogo debe estar vinculado a un profesional existente."
            )

    usuario = Usuario(
        email=datos.email,
        password_hash=security.hash_password(datos.password),
        rol=datos.rol,
        profesional_id=datos.profesional_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def verificar_rol(usuario: Usuario, rol: RolUsuario) -> Usuario:
    """Aplica RBAC por rol (RN-AU-03)."""
    if RolUsuario(usuario.rol) != rol:
        raise AccesoDenegadoError()
    return usuario


def verificar_profesional_own(usuario: Usuario, profesional_id: int) -> Usuario:
    """El odontólogo solo accede a su ``profesional_id``; admin puede todo."""
    if RolUsuario(usuario.rol) is RolUsuario.ADMIN:
        return usuario
    if (
        RolUsuario(usuario.rol) is not RolUsuario.ODONTOLOGO
        or usuario.profesional_id != profesional_id
    ):
        raise AccesoDenegadoError()
    return usuario
