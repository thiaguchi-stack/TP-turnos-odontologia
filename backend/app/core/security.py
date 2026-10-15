"""Capa de seguridad (stub).

Placeholder de la fundación para preparar la estructura de autenticación.
NO implementa lógica de autenticación ni JWT todavía: eso corresponde al
change C-03 (auth-jwt-rbac). Este módulo solo debe poder importarse sin
errores y no contiene secretos ni credenciales.
"""

from app.core.config import settings


def get_secret_key() -> str:
    """Devuelve la clave secreta configurada por entorno.

    Solo expone el valor ya cargado en ``settings``; la generación y el
    hashing de tokens se implementan en C-03.
    """
    return settings.secret_key
