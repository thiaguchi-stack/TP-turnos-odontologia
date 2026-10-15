import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, MixinAuditoria


class EstadoTurno(enum.StrEnum):
    """Estados admitidos para un turno (RN-TU-04)."""

    RESERVADO = "reservado"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"
    COMPLETADO = "completado"


# Alias de compatibilidad: los consumidores existentes importan ESTADOS_TURNO.
ESTADOS_TURNO = tuple(estado.value for estado in EstadoTurno)


class Turno(MixinAuditoria, Base):
    __tablename__ = "turno"
    __table_args__ = (
        Index("ix_turno_profesional_inicio", "profesional_id", "fecha_hora_inicio"),
        Index("ix_turno_sillon_inicio", "sillon_id", "fecha_hora_inicio"),
    )

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
            EstadoTurno,
            name="estado_turno",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda _: [estado.value for estado in EstadoTurno],
        ),
        default=EstadoTurno.RESERVADO,
        nullable=False,
    )
    token_cancelacion: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True
    )
    creado_por: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id"), nullable=True
    )
    cancelado_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)
