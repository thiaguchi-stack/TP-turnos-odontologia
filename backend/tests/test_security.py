from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_and_update, verify_password
from app.models import Usuario
from app.models.usuario import RolUsuario

CLAVE = "clave-secreta-de-prueba"

HASH_PBKDF2_LEGADO = (
    "pbkdf2_sha256$240000$fb55c920cc41d55f36b977f74b24f373$"
    "6c854f4895fb60062f9c4b6c6ef2da468397ae1cbdc13c7649dfdf72032f16e2"
)


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


def test_hash_password_usa_bcrypt_como_esquema_activo():
    hasheada = hash_password(CLAVE)

    assert hasheada.startswith("$2b$")
    assert CLAVE not in hasheada
    assert verify_password(CLAVE, hasheada) is True
    assert verify_password("clave-incorrecta", hasheada) is False


def test_verify_password_acepta_el_hash_pbkdf2_sembrado_por_c02():
    assert verify_password(CLAVE, HASH_PBKDF2_LEGADO) is True
    assert verify_password("clave-incorrecta", HASH_PBKDF2_LEGADO) is False


def test_hash_legado_se_rehashea_solo_en_el_primer_login_correcto():
    valido, nuevo_hash = verify_and_update(CLAVE, HASH_PBKDF2_LEGADO)

    assert valido is True
    assert nuevo_hash is not None
    assert nuevo_hash.startswith("$2b$")
    assert CLAVE not in nuevo_hash
    assert verify_password(CLAVE, nuevo_hash) is True

    valido_otra_vez, segundo_hash = verify_and_update(CLAVE, nuevo_hash)

    assert valido_otra_vez is True
    assert segundo_hash is None

    invalido, sin_hash = verify_and_update("clave-incorrecta", HASH_PBKDF2_LEGADO)

    assert invalido is False
    assert sin_hash is None
