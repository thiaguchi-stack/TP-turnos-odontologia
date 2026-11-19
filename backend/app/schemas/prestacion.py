from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    StrictBool,
    StrictInt,
    StringConstraints,
    field_validator,
)
from pydantic_core import PydanticCustomError

TextoCatalogo = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]


def _rechazar_duracion_no_positiva(valor: int | None) -> int | None:
    if valor is not None and valor <= 0:
        raise PydanticCustomError(
            "duracion_no_positiva", "La duración debe ser mayor que cero."
        )
    return valor


class PrestacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: TextoCatalogo
    duracion_minutos: StrictInt

    @field_validator("duracion_minutos")
    @classmethod
    def _duracion_positiva(cls, valor: int) -> int:
        return _rechazar_duracion_no_positiva(valor)


class PrestacionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: TextoCatalogo | None = None
    duracion_minutos: StrictInt | None = None
    activa: StrictBool | None = None

    @field_validator("duracion_minutos")
    @classmethod
    def _duracion_positiva(cls, valor: int | None) -> int | None:
        return _rechazar_duracion_no_positiva(valor)


class PrestacionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    nombre: str
    duracion_minutos: int
    activa: bool
