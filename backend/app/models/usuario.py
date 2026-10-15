import enum

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, MixinAuditoria


class RolUsuario(enum.StrEnum):
    """Roles admitidos para un usuario del sistema (RBAC en C-03)."""

    ADMIN = "admin"
    ODONTOLOGO = "odontologo"


class Usuario(MixinAuditoria, Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(
        Enum(
            RolUsuario,
            name="rol_usuario",
            native_enum=False,
            validate_strings=True,
            values_callable=lambda _: [rol.value for rol in RolUsuario],
        ),
        nullable=False,
    )
    # El vínculo 1:1 con Profesional es opcional a nivel de esquema; la regla
    # "rol odontólogo ⇒ profesional_id no nulo" se valida en C-03.
    profesional_id: Mapped[int | None] = mapped_column(
        ForeignKey("profesional.id"), nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
