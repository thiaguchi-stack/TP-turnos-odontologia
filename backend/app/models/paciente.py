from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, MixinAuditoria


class Paciente(MixinAuditoria, Base):
    __tablename__ = "paciente"
    __table_args__ = (
        UniqueConstraint("dni", "telefono", name="uq_paciente_dni_telefono"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    dni: Mapped[str] = mapped_column(String(20))
    telefono: Mapped[str] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(120))
    obsocial: Mapped[str | None] = mapped_column(String(100))

