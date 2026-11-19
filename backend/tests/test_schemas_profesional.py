from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.profesional import (
    ProfesionalCreate,
    ProfesionalRead,
    ProfesionalUpdate,
)


def test_profesional_read_expone_solo_los_cinco_campos_publicos():
    assert set(ProfesionalRead.model_fields) == {
        "id",
        "nombre",
        "apellido",
        "especialidad",
        "activo",
    }

    leido = ProfesionalRead.model_validate(
        {
            "id": 4,
            "nombre": "Ana",
            "apellido": "Rivas",
            "especialidad": "Ortodoncia",
            "activo": True,
        }
    )

    assert leido.model_dump() == {
        "id": 4,
        "nombre": "Ana",
        "apellido": "Rivas",
        "especialidad": "Ortodoncia",
        "activo": True,
    }


def test_profesional_create_activo_por_defecto_y_especialidad_opcional():
    creado = ProfesionalCreate(nombre="Ana", apellido="Rivas")

    assert creado.activo is True
    assert creado.especialidad is None

    con_especialidad = ProfesionalCreate(
        nombre="  Carla  ", apellido="Méndez", especialidad="Odontopediatría"
    )
    assert con_especialidad.nombre == "Carla"
    assert con_especialidad.especialidad == "Odontopediatría"


def test_profesional_create_rechaza_activo_no_booleano():
    with pytest.raises(ValidationError) as error:
        ProfesionalCreate(nombre="Ana", apellido="Rivas", activo="si")

    assert error.value.errors()[0]["type"] == "bool_type"

    with pytest.raises(ValidationError):
        ProfesionalCreate(nombre="Ana", apellido="Rivas", activo=1)


def test_profesional_create_rechaza_campos_extra():
    with pytest.raises(ValidationError) as error:
        ProfesionalCreate(id=99, nombre="Ana", apellido="Rivas")

    assert error.value.errors()[0]["type"] == "extra_forbidden"

    with pytest.raises(ValidationError):
        ProfesionalCreate(nombre="Ana", apellido="Rivas", estado="reservado")


def test_profesional_create_rechaza_nombre_vacio_y_apellido_solo_espacios():
    with pytest.raises(ValidationError):
        ProfesionalCreate(nombre="", apellido="Rivas")

    with pytest.raises(ValidationError):
        ProfesionalCreate(nombre="Ana", apellido="   ")

    with pytest.raises(ValidationError):
        ProfesionalCreate(nombre="A" * 101, apellido="Rivas")

    with pytest.raises(ValidationError):
        ProfesionalCreate(nombre="Ana", apellido="Rivas", especialidad="E" * 101)


def test_profesional_update_exige_al_menos_un_campo():
    with pytest.raises(ValidationError) as error:
        ProfesionalUpdate()

    assert "al menos un campo" in str(error.value)

    actualizacion = ProfesionalUpdate(especialidad="Endodoncia", activo=False)
    assert actualizacion.especialidad == "Endodoncia"
    assert actualizacion.activo is False
    assert actualizacion.nombre is None


def test_profesional_update_rechaza_campo_extra_y_activo_no_booleano():
    with pytest.raises(ValidationError) as error:
        ProfesionalUpdate(id=9)

    assert error.value.errors()[0]["type"] == "extra_forbidden"

    with pytest.raises(ValidationError):
        ProfesionalUpdate(activo="si")

    with pytest.raises(ValidationError):
        ProfesionalUpdate(nombre="")


def test_profesional_read_se_construye_desde_atributos_de_orm():
    objeto = SimpleNamespace(
        id=7,
        nombre="Jorge",
        apellido="Luna",
        especialidad="Endodoncia",
        activo=False,
        password_hash="hash-que-no-debe-salir",
    )

    leido = ProfesionalRead.model_validate(objeto)

    assert leido.activo is False
    assert "password_hash" not in leido.model_dump()
