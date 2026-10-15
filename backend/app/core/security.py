"""Capa de seguridad.

Incluye la clave secreta configurada por entorno y un **hash mínimo de
contraseñas** (PBKDF2-HMAC-SHA256 de la stdlib) para que el seed de C-02 pueda
persistir el admin sin contraseña en claro (RN-AU-04, OQ-4).

La autenticación real (JWT), el RBAC y la migración a bcrypt/argon2 quedan para
C-03; ``verify_password`` se conserva al migrar porque el formato del hash está
versionado.

Regla dura: **nunca** se loguea, imprime ni devuelve la contraseña en claro ni
el hash completo.
"""

import hashlib
import hmac
import os

from app.core.config import settings

#: Algoritmo de PBKDF2. Se guarda en el hash para poder migrar en C-03.
_ALGORITMO_PBKDF2 = "sha256"

#: Iteraciones de PBKDF2. Valor razonable para un hash de desarrollo local;
#: C-03 lo sube al recomendado de OWASP (600.000) al migrar a bcrypt/argon2.
_ITERACIONES_PBKDF2 = 240_000

#: Prefijo versionado del formato almacenado en ``password_hash``.
_PREFIJO_HASH = "pbkdf2_sha256"

#: Largo en bytes de la sal aleatoria por usuario.
_LARGO_SAL = 16


def get_secret_key() -> str:
    """Devuelve la clave secreta configurada por entorno.

    Solo expone el valor ya cargado en ``settings``; la generación y el
    hashing de tokens se implementan en C-03.
    """
    return settings.secret_key


def hash_password(password: str) -> str:
    """Devuelve un hash versionado de ``password`` con sal aleatoria.

    Formato: ``pbkdf2_sha256$<iteraciones>$<sal_hex>$<derivada_hex>``. La sal se
    genera con ``os.urandom`` en cada llamada, de modo que dos hashes de la
    misma contraseña difieren.
    """
    sal = os.urandom(_LARGO_SAL)
    derivada = hashlib.pbkdf2_hmac(
        _ALGORITMO_PBKDF2, password.encode("utf-8"), sal, _ITERACIONES_PBKDF2
    )
    return f"{_PREFIJO_HASH}${_ITERACIONES_PBKDF2}${sal.hex()}${derivada.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica ``password`` contra el hash almacenado.

    Devuelve ``False`` ante cualquier hash malformado o de otro esquema, sin
    filtrar información. La comparación es de tiempo constante.
    """
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
