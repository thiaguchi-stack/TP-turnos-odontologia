from pydantic import BaseModel, ConfigDict

from app.models.usuario import RolUsuario


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    rol: RolUsuario
    profesional_id: int | None


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str
    rol: RolUsuario
    profesional_id: int | None = None
