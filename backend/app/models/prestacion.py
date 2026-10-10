from sqlalchemy import Boolean, CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Prestacion(Base):
    __tablename__ = "prestacion"
    __table_args__ = (
        CheckConstraint("duracion_minutos > 0", name="ck_prestacion_duracion"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    duracion_minutos: Mapped[int] = mapped_column(Integer)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
