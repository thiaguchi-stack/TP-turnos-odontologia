from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    StrictBool,
    StringConstraints,
    model_validator,
)
from pydantic_core import PydanticCustomError

TextoCatalogo = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]
EspecialidadCatalogo = Annotated[
    str, StringConstraints(strip_whitespace=True, max_length=100)
]


class ProfesionalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: TextoCatalogo
    apellido: TextoCatalogo
    especialidad: EspecialidadCatalogo | None = None
    activo: StrictBool = True


class ProfesionalUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: TextoCatalogo | None = None
    apellido: TextoCatalogo | None = None
    especialidad: EspecialidadCatalogo | None = None
    activo: StrictBool | None = None

    @model_validator(mode="after")
    def _al_menos_un_campo(self) -> "ProfesionalUpdate":
        if all(
            getattr(self, campo) is None
            for campo in ("nombre", "apellido", "especialidad", "activo")
        ):
            raise PydanticCustomError(
                "campo_requerido",
                "Debe enviarse al menos un campo para actualizar.",
            )
        return self


class ProfesionalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    nombre: str
    apellido: str
    especialidad: str | None
    activo: bool
