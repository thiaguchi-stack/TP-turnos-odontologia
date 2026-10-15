from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core import clock
from app.db.base import Base

ESTADOS_TURNO = ("reservado", "confirmado", "cancelado", "completado")


class Turno(Base):
    __tablename__ = "turno"

    id: Mapped[int] = mapped_column(primary_key=True)
    profesional_id: Mapped[int] = mapped_column(
        ForeignKey("profesional.id"), nullable=False
    )
    paciente_id: Mapped[int] = mapped_column(ForeignKey("paciente.id"), nullable=False)
    prestacion_id: Mapped[int] = mapped_column(
        ForeignKey("prestacion.id"), nullable=False
    )
    sillon_id: Mapped[int] = mapped_column(ForeignKey("sillon.id"), nullable=False)
    fecha_hora_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_hora_fin: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    estado: Mapped[str] = mapped_column(
        Enum(
            *ESTADOS_TURNO,
            name="estado_turno",
            native_enum=False,
            validate_strings=True,
        ),
        default="reservado",
        nullable=False,
    )
    token_cancelacion: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=lambda: clock.now())
    cancelado_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)
