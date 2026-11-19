from collections.abc import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Usuario
from app.models.usuario import RolUsuario
from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Usuario:
    """Resuelve el usuario autenticado en cada request desde la DB."""
    return auth_service.usuario_desde_token(db, token)


def require_role(rol: RolUsuario) -> Callable[..., Usuario]:
    """Factoría de dependencias que exige un rol concreto."""

    def dependency(
        usuario: Usuario = Depends(get_current_user),
    ) -> Usuario:
        return auth_service.verificar_rol(usuario, rol)

    return dependency


def require_odontologo_own(
    profesional_id: int, usuario: Usuario = Depends(get_current_user)
) -> Usuario:
    """Exige odontólogo dueño de ``profesional_id`` o admin (RN-AU-02/03)."""
    return auth_service.verificar_profesional_own(usuario, profesional_id)
