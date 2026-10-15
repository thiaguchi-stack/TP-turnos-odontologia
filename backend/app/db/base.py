from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core import clock


class Base(DeclarativeBase):
    pass


class MixinAuditoria:
    """Agrega el campo de auditoría ``creado_en``.

    El valor por defecto se toma del reloj central (``clock.now()``) para que
    los tests puedan controlarlo con ``unittest.mock.patch`` de forma
    determinista.
    """

    creado_en: Mapped[datetime] = mapped_column(DateTime, default=lambda: clock.now())
