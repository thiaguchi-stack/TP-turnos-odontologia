from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Bloqueo(Base):
    __tablename__ = "bloqueo"
    __table_args__ = (
        Index("ix_bloqueo_profesional_inicio", "profesional_id", "fecha_hora_inicio"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    profesional_id: Mapped[int] = mapped_column(
        ForeignKey("profesional.id"), nullable=False
    )
    sillon_id: Mapped[int | None] = mapped_column(
        ForeignKey("sillon.id"), nullable=True
    )
    fecha_hora_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_hora_fin: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    motivo: Mapped[str | None] = mapped_column(String(200), nullable=True)
