from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.seed import (
    EMAIL_ADMIN,
    EMAIL_ODONTOLOGO,
    PASSWORD_ADMIN,
    seed_minimo,
)
from app.models import Paciente, Profesional, Usuario
from app.models.usuario import RolUsuario


def _contar(db: Session, modelo: type) -> int:
    return db.scalar(select(func.count()).select_from(modelo)) or 0


def test_seed_en_base_vacia_crea_admin_profesional_y_odontologo_vinculado(db: Session):
    seed_minimo(db)

    admin = db.scalar(select(Usuario).where(Usuario.email == EMAIL_ADMIN))
    odontologo = db.scalar(select(Usuario).where(Usuario.email == EMAIL_ODONTOLOGO))
    profesional = db.scalar(
        select(Profesional).where(Profesional.id == odontologo.profesional_id)
    )

    assert admin is not None
    assert admin.rol == RolUsuario.ADMIN
    assert admin.profesional_id is None
    assert admin.activo is True

    assert odontologo is not None
    assert odontologo.rol == RolUsuario.ODONTOLOGO
    assert profesional is not None
    assert profesional.activo is True


def test_seed_persiste_hash_que_valida_la_clave_sin_guardarla_en_claro(db: Session):
    seed_minimo(db)

    admin = db.scalar(select(Usuario).where(Usuario.email == EMAIL_ADMIN))

    assert admin.password_hash != PASSWORD_ADMIN
    assert PASSWORD_ADMIN not in admin.password_hash
    assert verify_password(PASSWORD_ADMIN, admin.password_hash) is True


def test_seed_ejecutado_dos_veces_no_duplica_ni_altera_existentes(db: Session):
    seed_minimo(db)
    admin_antes = db.scalar(select(Usuario).where(Usuario.email == EMAIL_ADMIN))
    hash_admin_antes = admin_antes.password_hash
    odontologo_antes = db.scalar(
        select(Usuario).where(Usuario.email == EMAIL_ODONTOLOGO)
    )
    profesional_id_antes = odontologo_antes.profesional_id

    seed_minimo(db)

    assert _contar(db, Usuario) == 2
    assert _contar(db, Profesional) == 1
    assert _contar(db, Paciente) == 1

    admin_despues = db.scalar(select(Usuario).where(Usuario.email == EMAIL_ADMIN))
    odontologo_despues = db.scalar(
        select(Usuario).where(Usuario.email == EMAIL_ODONTOLOGO)
    )
    assert admin_despues.password_hash == hash_admin_antes
    assert odontologo_despues.profesional_id == profesional_id_antes
