from datetime import time

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HorarioAtencion(Base):
    __tablename__ = "horario_atencion"
    __table_args__ = (
        CheckConstraint("hora_fin > hora_inicio", name="ck_horario_atencion_franja"),
        CheckConstraint(
            "dia_semana >= 0 AND dia_semana <= 6",
            name="ck_horario_atencion_dia_semana",
        ),
        UniqueConstraint(
            "profesional_id",
            "dia_semana",
            "hora_inicio",
            name="uq_horario_atencion_franja",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    profesional_id: Mapped[int] = mapped_column(
        ForeignKey("profesional.id"), nullable=False
    )
    dia_semana: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # ISO 0–6 (lunes=0)  # noqa: E501
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
