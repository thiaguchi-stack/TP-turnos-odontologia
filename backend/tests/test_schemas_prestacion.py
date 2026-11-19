from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.prestacion import PrestacionCreate, PrestacionRead, PrestacionUpdate


def test_prestacion_create_acepta_nombre_y_duracion_valida():
    datos = PrestacionCreate(nombre="Limpieza", duracion_minutos=30)

    assert datos.model_dump() == {"nombre": "Limpieza", "duracion_minutos": 30}


@pytest.mark.parametrize("duracion", [0, -5])
def test_prestacion_create_rechaza_duracion_no_positiva(duracion):
    with pytest.raises(ValidationError, match="mayor que cero"):
        PrestacionCreate(nombre="Limpieza", duracion_minutos=duracion)


def test_prestacion_create_rechaza_campo_extra():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        PrestacionCreate(nombre="Limpieza", duracion_minutos=30, estado="activa")


def test_prestacion_update_acepta_campos_opcionales_y_parciales():
    cambios = PrestacionUpdate(nombre="Limpieza profunda", activa=False)

    assert cambios.model_dump(exclude_unset=True) == {
        "nombre": "Limpieza profunda",
        "activa": False,
    }
    solo_duracion = PrestacionUpdate(duracion_minutos=45)
    assert solo_duracion.model_dump(exclude_unset=True) == {"duracion_minutos": 45}


@pytest.mark.parametrize("duracion", [0, -5])
def test_prestacion_update_rechaza_duracion_no_positiva(duracion):
    with pytest.raises(ValidationError, match="mayor que cero"):
        PrestacionUpdate(duracion_minutos=duracion)


def test_prestacion_update_rechaza_campo_extra():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        PrestacionUpdate(duracion_minutos=30, id=99)


def test_duracion_rechaza_valores_no_enteros():
    with pytest.raises(ValidationError):
        PrestacionCreate(nombre="Limpieza", duracion_minutos="30")
    with pytest.raises(ValidationError):
        PrestacionUpdate(duracion_minutos=30.5)


def test_prestacion_read_expone_solo_campos_del_catalogo():
    assert set(PrestacionRead.model_fields) == {
        "id",
        "nombre",
        "duracion_minutos",
        "activa",
    }

    leida = PrestacionRead.model_validate(
        SimpleNamespace(
            id=7,
            nombre="Limpieza",
            duracion_minutos=30,
            activa=True,
            password_hash="secreto-ficticio",
        )
    )

    assert leida.model_dump() == {
        "id": 7,
        "nombre": "Limpieza",
        "duracion_minutos": 30,
        "activa": True,
    }
