from datetime import datetime, timedelta
from typing import Literal, TypeVar

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core import clock
from app.db.base import Base
from app.models import Bloqueo, Paciente, Prestacion, Profesional, Sillon, Turno
from app.services.errores import TurnoRechazadoError, TurnoSolapadoError

MotivoSolapamiento = Literal["profesional", "sillón", "bloqueo"]
ModeloT = TypeVar("ModeloT", bound=Base)


def _existe_o_rechaza(
    db: Session, modelo: type[ModeloT], entidad_id: int, nombre: str
) -> ModeloT:
    entidad = db.get(modelo, entidad_id)
    if entidad is None:
        raise TurnoRechazadoError(f"No existe {nombre} con id {entidad_id}.")
    return entidad


def _detectar_motivo_solapamiento(
    db: Session,
    *,
    profesional_id: int,
    sillon_id: int,
    inicio: datetime,
    fin: datetime,
) -> MotivoSolapamiento | None:
    turnos_solapados = select(Turno).where(
        Turno.estado != "cancelado",
        Turno.fecha_hora_inicio < fin,
        Turno.fecha_hora_fin > inicio,
    )

    if db.scalar(
        turnos_solapados.where(Turno.profesional_id == profesional_id).limit(1)
    ):
        return "profesional"

    if db.scalar(turnos_solapados.where(Turno.sillon_id == sillon_id).limit(1)):
        return "sillón"

    bloqueo_solapado = db.scalar(
        select(Bloqueo)
        .where(
            Bloqueo.profesional_id == profesional_id,
            or_(Bloqueo.sillon_id.is_(None), Bloqueo.sillon_id == sillon_id),
            Bloqueo.fecha_hora_inicio < fin,
            Bloqueo.fecha_hora_fin > inicio,
        )
        .limit(1)
    )
    if bloqueo_solapado is not None:
        return "bloqueo"

    return None


def crear_turno(
    db: Session,
    *,
    profesional_id: int,
    paciente_id: int,
    prestacion_id: int,
    sillon_id: int,
    fecha_hora_inicio: datetime,
) -> Turno:
    profesional = _existe_o_rechaza(db, Profesional, profesional_id, "el profesional")
    paciente = _existe_o_rechaza(db, Paciente, paciente_id, "el paciente")
    prestacion = _existe_o_rechaza(db, Prestacion, prestacion_id, "la prestación")
    sillon = _existe_o_rechaza(db, Sillon, sillon_id, "el sillón")

    if not profesional.activo:
        raise TurnoRechazadoError(
            "El profesional está inactivo y no recibe turnos nuevos."
        )
    if not sillon.activo:
        raise TurnoRechazadoError("El sillón está inactivo y no recibe turnos nuevos.")
    if not prestacion.activa:
        raise TurnoRechazadoError(
            "La prestación está inactiva y no admite turnos nuevos."
        )

    # RN-TU-06 / spec «Sin turnos en el pasado»: se juzga por fecha_hora_inicio
    # (inicio < ahora); un turno "en curso" (inicio pasado, fin derivado futuro)
    # también se rechaza. La lectura `fin < ahora` de la KB (05_reglas_de_negocio)
    # gobierna las transiciones de estado de RN-TU-06, no esta creación.
    if fecha_hora_inicio < clock.now():
        raise TurnoRechazadoError("No se puede crear un turno en el pasado.")

    fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=prestacion.duracion_minutos)

    motivo = _detectar_motivo_solapamiento(
        db,
        profesional_id=profesional.id,
        sillon_id=sillon.id,
        inicio=fecha_hora_inicio,
        fin=fecha_hora_fin,
    )
    if motivo is not None:
        raise TurnoSolapadoError(motivo)

    turno = Turno(
        profesional_id=profesional.id,
        paciente_id=paciente.id,
        prestacion_id=prestacion.id,
        sillon_id=sillon.id,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        estado="reservado",
    )
    db.add(turno)
    db.commit()
    return turno
