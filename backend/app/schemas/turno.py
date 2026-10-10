from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TurnoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profesional_id: int
    paciente_id: int
    prestacion_id: int
    sillon_id: int
    fecha_hora_inicio: datetime


class TurnoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    profesional_id: int
    paciente_id: int
    prestacion_id: int
    sillon_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str
