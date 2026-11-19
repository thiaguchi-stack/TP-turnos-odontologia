"""Capa de seguridad: hash de contraseñas, JWT y configuración de firma.

El esquema activo es bcrypt (RN-AU-04). El hash versionado ``pbkdf2_sha256``
sembrado por C-02 se conserva solo como legado: se verifica y se rehashea en el
primer login correcto. Nunca se loguea, imprime ni devuelve la contraseña en
claro ni el hash completo.
"""

import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import cast

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.services.errores import TokenExpiradoError, TokenInvalidoError

#: Esquema activo y único de ``CryptContext``; el legado se verifica aparte.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#: Parámetros del hash PBKDF2 versionado que generó C-02.
_ALGORITMO_PBKDF2 = "sha256"
_PREFIJO_HASH = "pbkdf2_sha256"
_LARGO_SAL = 16


def get_secret_key() -> str:
    """Devuelve la clave secreta configurada por entorno."""
    return settings.secret_key


def get_token_expire_min() -> int:
    """Devuelve la vigencia del token en minutos configurada por entorno."""
    return settings.token_expire_min


def create_access_token(
    claims: dict[str, object], expires_delta: timedelta | None = None
) -> str:
    """Firma un JWT HS256 con los claims recibidos y ``exp`` derivado."""
    datos = dict(claims)
    vigencia = get_token_expire_min() if expires_delta is None else (
        expires_delta.total_seconds() / 60
    )
    datos["exp"] = datetime.now(UTC) + timedelta(minutes=vigencia)
    return jwt.encode(datos, get_secret_key(), algorithm="HS256")


def decode_access_token(token: str) -> dict[str, object]:
    """Decodifica y valida firma y expiración de un JWT HS256."""
    try:
        return cast(
            dict[str, object],
            jwt.decode(token, get_secret_key(), algorithms=["HS256"]),
        )
    except jwt.ExpiredSignatureError as error:
        raise TokenExpiradoError() from error
    except jwt.InvalidTokenError as error:
        raise TokenInvalidoError() from error


def hash_password(password: str) -> str:
    """Devuelve un hash bcrypt de ``password`` con sal aleatoria."""
    return pwd_context.hash(password)


def _es_hash_legado(password_hash: str) -> bool:
    return isinstance(password_hash, str) and password_hash.startswith(
        f"{_PREFIJO_HASH}$"
    )


def _verificar_pbkdf2_legado(password: str, password_hash: str) -> bool:
    try:
        prefijo, iteraciones_txt, sal_hex, hash_hex = password_hash.split("$")
        iteraciones = int(iteraciones_txt)
        sal = bytes.fromhex(sal_hex)
        esperada = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False

    if prefijo != _PREFIJO_HASH or iteraciones <= 0:
        return False

    derivada = hashlib.pbkdf2_hmac(
        _ALGORITMO_PBKDF2, password.encode("utf-8"), sal, iteraciones
    )
    return hmac.compare_digest(derivada, esperada)


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica ``password`` contra un hash bcrypt activo o PBKDF2 legado."""
    if _es_hash_legado(password_hash):
        return _verificar_pbkdf2_legado(password, password_hash)
    try:
        return bool(pwd_context.verify(password, password_hash))
    except (ValueError, TypeError):
        return False


def verify_and_update(
    password: str, password_hash: str
) -> tuple[bool, str | None]:
    """Verifica y devuelve un hash nuevo solo si el legado debe migrarse."""
    if _es_hash_legado(password_hash):
        if not _verificar_pbkdf2_legado(password, password_hash):
            return False, None
        return True, hash_password(password)
    try:
        valido, actualizado = pwd_context.verify_and_update(password, password_hash)
    except (ValueError, TypeError):
        return False, None
    return bool(valido), actualizado
