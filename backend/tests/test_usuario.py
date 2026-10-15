import pytest
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Profesional, Usuario
from app.models.usuario import RolUsuario


@pytest.fixture(autouse=True)
def _esquema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_usuario_admin_con_profesional_id_nulo_se_persiste():
    with SessionLocal() as db:
        usuario = Usuario(
            email="admin@clinica.local",
            password_hash="pbkdf2$100000$sal$hash",
            rol=RolUsuario.ADMIN,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    assert usuario.id is not None
    assert usuario.profesional_id is None
    assert usuario.activo is True


def test_usuario_odontologo_con_profesional_existente_se_persiste():
    with SessionLocal() as db:
        profesional = Profesional(
            nombre="Ana", apellido="Rivas", especialidad="Ortodoncia"
        )
        db.add(profesional)
        db.commit()
        profesional_id = profesional.id

        usuario = Usuario(
            email="odontologo@clinica.local",
            password_hash="pbkdf2$100000$sal$hash",
            rol=RolUsuario.ODONTOLOGO,
            profesional_id=profesional_id,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)

    assert usuario.profesional_id == profesional_id


def test_email_unico_rechaza_segundo_usuario():
    with SessionLocal() as db:
        u1 = Usuario(
            email="admin@clinica.local",
            password_hash="pbkdf2$100000$sal$hash1",
            rol=RolUsuario.ADMIN,
        )
        db.add(u1)
        db.commit()

        u2 = Usuario(
            email="admin@clinica.local",
            password_hash="pbkdf2$100000$sal$hash2",
            rol=RolUsuario.ADMIN,
        )
        db.add(u2)
        with pytest.raises(IntegrityError):
            db.commit()


def test_profesional_id_inexistente_rechazado_por_fk():
    with SessionLocal() as db:
        usuario = Usuario(
            email="odontologo@clinica.local",
            password_hash="pbkdf2$100000$sal$hash",
            rol=RolUsuario.ODONTOLOGO,
            profesional_id=999,
        )
        db.add(usuario)
        with pytest.raises(IntegrityError):
            db.commit()

