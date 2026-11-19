from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Prestacion
from app.schemas.prestacion import PrestacionCreate, PrestacionUpdate
from app.services.errores import PrestacionNoEncontradaError, PrestacionRechazadaError


def _validar_duracion(duracion: int) -> None:
    if duracion <= 0:
        raise PrestacionRechazadaError("La duración debe ser mayor que cero.")


def crear(db: Session, datos: PrestacionCreate) -> Prestacion:
    _validar_duracion(datos.duracion_minutos)
    prestacion = Prestacion(**datos.model_dump())
    db.add(prestacion)
    db.commit()
    db.refresh(prestacion)
    return prestacion


def listar_activas(db: Session) -> list[Prestacion]:
    return list(
        db.scalars(
            select(Prestacion)
            .where(Prestacion.activa.is_(True))
            .order_by(Prestacion.id)
        ).all()
    )


def actualizar(
    db: Session, prestacion_id: int, datos: PrestacionUpdate
) -> Prestacion:
    prestacion = db.get(Prestacion, prestacion_id)
    if prestacion is None:
        raise PrestacionNoEncontradaError(
            f"No existe la prestación con id {prestacion_id}."
        )

    cambios = datos.model_dump(exclude_unset=True)
    if "duracion_minutos" in cambios:
        _validar_duracion(cambios["duracion_minutos"])
    for campo, valor in cambios.items():
        setattr(prestacion, campo, valor)

    db.add(prestacion)
    db.commit()
    db.refresh(prestacion)
    return prestacion
