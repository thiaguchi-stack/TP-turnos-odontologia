from pathlib import Path

PYPROJECT = Path(__file__).parents[1].joinpath("pyproject.toml")


def test_dependencias_de_auth_declaradas_en_pyproject():
    contenido = PYPROJECT.read_text(encoding="utf-8")

    assert '"passlib' in contenido
    assert '"bcrypt' in contenido
    assert '"PyJWT' in contenido


def test_bibliotecas_de_auth_importables_y_operativas():
    import jwt
    from passlib.context import CryptContext

    contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash_bcrypt = contexto.hash("clave-ficticia-de-prueba")

    assert hash_bcrypt.startswith("$2b$")
    assert contexto.verify("clave-ficticia-de-prueba", hash_bcrypt) is True

    clave = "clave-ficticia-de-prueba-con-longitud-suficiente-32bytes"
    token = jwt.encode({"sub": "7", "rol": "admin"}, clave, algorithm="HS256")
    decodificado = jwt.decode(token, clave, algorithms=["HS256"])

    assert decodificado["sub"] == "7"
    assert decodificado["rol"] == "admin"
