from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import Usuario
from app.models.usuario import RolUsuario

CLAVE = "clave-secreta-de-prueba"


def test_hash_password_no_es_igual_ni_contiene_la_clave_en_claro():
    hasheada = hash_password(CLAVE)

    assert hasheada != CLAVE
    assert CLAVE not in hasheada


def test_hash_password_genera_sal_aleatoria_distinta_por_llamada():
    assert hash_password(CLAVE) != hash_password(CLAVE)


def test_verify_password_valida_la_correcta_y_rechaza_la_incorrecta():
    hasheada = hash_password(CLAVE)

    assert verify_password(CLAVE, hasheada) is True
    assert verify_password("otra-clave", hasheada) is False


def test_verify_password_rechaza_hashes_malformados():
    assert verify_password(CLAVE, "") is False
    assert verify_password(CLAVE, "texto-plano") is False
    assert verify_password(CLAVE, "pbkdf2_sha256$abc$zz$zz") is False
    assert verify_password(CLAVE, "bcrypt$12$sal$hash") is False


def test_repr_de_usuario_no_expone_password_hash():
    usuario = Usuario(
        email="admin@clinica.local",
        password_hash=hash_password(CLAVE),
        rol=RolUsuario.ADMIN,
    )

    representacion = repr(usuario)

    assert CLAVE not in representacion
    assert usuario.password_hash not in representacion


def test_password_hash_persistido_difiere_de_la_clave_en_claro(db: Session):
    usuario = Usuario(
        email="admin@clinica.local",
        password_hash=hash_password(CLAVE),
        rol=RolUsuario.ADMIN,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    assert usuario.password_hash != CLAVE
    assert CLAVE not in usuario.password_hash
    assert verify_password(CLAVE, usuario.password_hash) is True
