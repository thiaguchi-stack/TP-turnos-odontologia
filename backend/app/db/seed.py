"""Seed mínimo e idempotente de datos ficticios (RN-DATOS-03).

Crea, si no existen, un usuario admin, un profesional activo con su usuario
odontólogo vinculado y un paciente de contacto. Está pensado para que C-03
(login/RBAC) tenga con qué arrancar sin datos reales.

``seed_minimo`` es una función pura y testeable (no depende del startup HTTP):
se invoca desde el ``lifespan`` de ``app/main.py`` y también directo en tests.
Es idempotente: hace *lookup* por ``email`` (usuarios), ``(nombre, apellido)``
(profesional) y ``(dni, telefono)`` (paciente) antes de insertar.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Paciente, Profesional, Usuario
from app.models.usuario import RolUsuario

# Credenciales *ficticias* de desarrollo (no son secretos reales). C-03 reemplaza
# este flujo por usuarios gestionados y contraseñas productivas; aquí solo se
# persiste el hash (nunca la contraseña en claro).
EMAIL_ADMIN = "admin@clinica.local"
PASSWORD_ADMIN = "admin-local-cambiar"
EMAIL_ODONTOLOGO = "odontologo@clinica.local"
PASSWORD_ODONTOLOGO = "odonto-local-cambiar"

PROFESIONAL_NOMBRE = "Marta"
PROFESIONAL_APELLIDO = "Gómez"
PROFESIONAL_ESPECIALIDAD = "Clínica general"

PACIENTE_NOMBRE = "Sofía"
PACIENTE_APELLIDO = "Ramírez"
PACIENTE_DNI = "33444555"
PACIENTE_TELEFONO = "1144440000"


def _obtener_o_crear_profesional(db: Session) -> Profesional:
    profesional = db.scalar(
        select(Profesional).where(
            Profesional.nombre == PROFESIONAL_NOMBRE,
            Profesional.apellido == PROFESIONAL_APELLIDO,
        )
    )
    if profesional is None:
        profesional = Profesional(
            nombre=PROFESIONAL_NOMBRE,
            apellido=PROFESIONAL_APELLIDO,
            especialidad=PROFESIONAL_ESPECIALIDAD,
        )
        db.add(profesional)
        db.flush()
    return profesional


def _obtener_o_crear_usuario(
    db: Session,
    *,
    email: str,
    password: str,
    rol: RolUsuario,
    profesional_id: int | None = None,
) -> Usuario:
    usuario = db.scalar(select(Usuario).where(Usuario.email == email))
    if usuario is None:
        usuario = Usuario(
            email=email,
            password_hash=hash_password(password),
            rol=rol,
            profesional_id=profesional_id,
        )
        db.add(usuario)
    return usuario


def _obtener_o_crear_paciente(db: Session) -> Paciente:
    paciente = db.scalar(
        select(Paciente).where(
            Paciente.dni == PACIENTE_DNI,
            Paciente.telefono == PACIENTE_TELEFONO,
        )
    )
    if paciente is None:
        paciente = Paciente(
            nombre=PACIENTE_NOMBRE,
            apellido=PACIENTE_APELLIDO,
            dni=PACIENTE_DNI,
            telefono=PACIENTE_TELEFONO,
        )
        db.add(paciente)
    return paciente


def seed_minimo(db: Session) -> None:
    """Garantiza las entidades mínimas sin duplicar registros existentes.

    No modifica registros ya presentes: si el admin existe, no re-hashea su
    contraseña ni altera su rol.
    """
    profesional = _obtener_o_crear_profesional(db)
    _obtener_o_crear_usuario(
        db,
        email=EMAIL_ADMIN,
        password=PASSWORD_ADMIN,
        rol=RolUsuario.ADMIN,
    )
    _obtener_o_crear_usuario(
        db,
        email=EMAIL_ODONTOLOGO,
        password=PASSWORD_ODONTOLOGO,
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=profesional.id,
    )
    _obtener_o_crear_paciente(db)
    db.commit()
