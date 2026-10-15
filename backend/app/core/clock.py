"""Reloj único de la aplicación.

Convención de zona horaria: fecha y hora **naive** (sin ``tzinfo``) en la
hora **local** del sistema — Argentina, consultorio single-tenant — con el
mismo significado que ``datetime.now()``. SQLite persiste ``DateTime`` naive
y la API recibe ``fecha_hora_inicio`` naive desde el frontend (zona horaria
local del consultorio), así que el reloj central mantiene ese comportamiento
para no cambiar ningún comportamiento existente.

Todos los call sites que necesiten "la hora actual" (servicio y defaults de
modelos) deben leerla desde ``clock.now()`` — vía referencia al módulo
(``from app.core import clock``) — para que los tests puedan controlar el
reloj con ``unittest.mock.patch("app.core.clock.now", ...)`` de forma
determinista.
"""

from datetime import datetime


def now() -> datetime:
    """Devuelve la hora actual local naive (sin ``tzinfo``)."""
    return datetime.now()
