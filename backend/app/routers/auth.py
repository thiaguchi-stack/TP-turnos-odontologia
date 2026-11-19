"""Routers delgados de autenticación: solo delegan en el servicio."""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models import Usuario
from app.models.usuario import RolUsuario
from app.schemas.auth import TokenRead, UsuarioCreate, UsuarioRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenRead)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenRead:
    ip = request.client.host if request.client is not None else "local"
    usuario = auth_service.autenticar(db, form.username, form.password, ip=ip)
    return auth_service.emitir_token(usuario)


@router.get("/me", response_model=UsuarioRead)
def me(usuario: Usuario = Depends(get_current_user)) -> UsuarioRead:
    return UsuarioRead.model_validate(usuario)


@router.post("/usuarios", status_code=201, response_model=UsuarioRead)
def crear_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_role(RolUsuario.ADMIN)),
) -> UsuarioRead:
    usuario = auth_service.crear_usuario(db, payload)
    return UsuarioRead.model_validate(usuario)


