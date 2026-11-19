"""Routers delgados del catálogo de profesionales: solo delegan en el servicio."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models import Usuario
from app.models.usuario import RolUsuario
from app.schemas.profesional import (
    ProfesionalCreate,
    ProfesionalRead,
    ProfesionalUpdate,
)
from app.services import profesional_service
from app.services.errores import (
    ProfesionalNoEncontradoError,
    ProfesionalRechazadoError,
)

router = APIRouter(prefix="/profesionales", tags=["profesionales"])


@router.get("", response_model=list[ProfesionalRead])
def listar(db: Session = Depends(get_db)) -> list[ProfesionalRead]:
    profesionales = profesional_service.listar_activos(db)
    return [
        ProfesionalRead.model_validate(profesional) for profesional in profesionales
    ]


@router.get("/{profesional_id}", response_model=ProfesionalRead)
def detalle(profesional_id: int, db: Session = Depends(get_db)) -> ProfesionalRead:
    try:
        profesional = profesional_service.obtener_activo(db, profesional_id)
    except ProfesionalNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=error.motivo) from error
    return ProfesionalRead.model_validate(profesional)


@router.post("", status_code=201, response_model=ProfesionalRead)
def crear_profesional(
    payload: ProfesionalCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_role(RolUsuario.ADMIN)),
) -> ProfesionalRead:
    profesional = profesional_service.crear(db, payload)
    return ProfesionalRead.model_validate(profesional)


@router.put("/{profesional_id}", response_model=ProfesionalRead)
def editar_profesional(
    profesional_id: int,
    payload: ProfesionalUpdate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_role(RolUsuario.ADMIN)),
) -> ProfesionalRead:
    try:
        profesional = profesional_service.actualizar(db, profesional_id, payload)
    except ProfesionalNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=error.motivo) from error
    except ProfesionalRechazadoError as error:
        raise HTTPException(status_code=400, detail=error.motivo) from error
    return ProfesionalRead.model_validate(profesional)


@router.delete("/{profesional_id}", response_model=ProfesionalRead)
def bajar_profesional(
    profesional_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_role(RolUsuario.ADMIN)),
) -> ProfesionalRead:
    try:
        profesional = profesional_service.desactivar(db, profesional_id)
    except ProfesionalNoEncontradoError as error:
        raise HTTPException(status_code=404, detail=error.motivo) from error
    except ProfesionalRechazadoError as error:
        raise HTTPException(status_code=400, detail=error.motivo) from error
    return ProfesionalRead.model_validate(profesional)
