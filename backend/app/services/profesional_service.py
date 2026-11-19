from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Profesional
from app.schemas.profesional import ProfesionalCreate, ProfesionalUpdate
from app.services.errores import ProfesionalNoEncontradoError


def crear(db: Session, datos: ProfesionalCreate) -> Profesional:
    profesional = Profesional(**datos.model_dump())
    db.add(profesional)
    db.commit()
    db.refresh(profesional)
    return profesional


def actualizar(
    db: Session, profesional_id: int, datos: ProfesionalUpdate
) -> Profesional:
    profesional = db.get(Profesional, profesional_id)
    if profesional is None:
        raise ProfesionalNoEncontradoError(
            f"No existe el profesional con id {profesional_id}."
        )
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(profesional, campo, valor)
    db.add(profesional)
    db.commit()
    db.refresh(profesional)
    return profesional


def desactivar(db: Session, profesional_id: int) -> Profesional:
    profesional = db.get(Profesional, profesional_id)
    if profesional is None:
        raise ProfesionalNoEncontradoError(
            f"No existe el profesional con id {profesional_id}."
        )
    if profesional.activo:
        profesional.activo = False
        db.add(profesional)
        db.commit()
        db.refresh(profesional)
    return profesional


def listar_activos(db: Session) -> list[Profesional]:
    return list(
        db.scalars(
            select(Profesional)
            .where(Profesional.activo.is_(True))
            .order_by(Profesional.id)
        ).all()
    )


def obtener_activo(db: Session, profesional_id: int) -> Profesional:
    profesional = db.get(Profesional, profesional_id)
    if profesional is None or not profesional.activo:
        raise ProfesionalNoEncontradoError(
            f"No existe un profesional activo con id {profesional_id}."
        )
    return profesional
