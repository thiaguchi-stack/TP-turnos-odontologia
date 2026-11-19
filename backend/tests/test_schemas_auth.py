import pytest
from pydantic import ValidationError

from app.models.usuario import RolUsuario
from app.schemas.auth import TokenRead, UsuarioCreate, UsuarioRead


def test_usuario_read_no_expone_password_hash():
    assert "password_hash" not in UsuarioRead.model_fields
    assert set(UsuarioRead.model_fields) == {
        "id",
        "email",
        "rol",
        "profesional_id",
    }

    leido = UsuarioRead(
        id=3,
        email="odontologo@clinica.local",
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=9,
    )

    assert leido.model_dump() == {
        "id": 3,
        "email": "odontologo@clinica.local",
        "rol": RolUsuario.ODONTOLOGO,
        "profesional_id": 9,
    }


def test_token_read_y_creacion_de_usuario_con_campos_explicitos():
    token = TokenRead(access_token="token-ficticio")

    assert token.token_type == "Bearer"
    assert token.model_dump() == {
        "access_token": "token-ficticio",
        "token_type": "Bearer",
    }

    creacion = UsuarioCreate(
        email="nuevo@clinica.local",
        password="clave-ficticia-nueva",
        rol=RolUsuario.ODONTOLOGO,
        profesional_id=4,
    )

    assert creacion.rol == RolUsuario.ODONTOLOGO
    assert creacion.profesional_id == 4

    with pytest.raises(ValidationError):
        UsuarioCreate(
            email="nuevo@clinica.local",
            password="clave-ficticia-nueva",
            rol=RolUsuario.ADMIN,
            password_hash="hash-inyectado",
        )
