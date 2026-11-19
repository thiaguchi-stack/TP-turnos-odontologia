"""Routers delgados del catálogo de prestaciones: solo delegan en el servicio."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models import Usuario
from app.models.usuario import RolUsuario
from app.schemas.prestacion import PrestacionCreate, PrestacionRead, PrestacionUpdate
from app.services import prestacion_service
from app.services.errores import (
    PrestacionNoEncontradaError,
    PrestacionRechazadaError,
)

router = APIRouter(prefix="/prestaciones", tags=["prestaciones"])


@router.get("", response_model=list[PrestacionRead])
def listar(db: Session = Depends(get_db)) -> list[PrestacionRead]:
    prestaciones = prestacion_service.listar_activas(db)
    return [PrestacionRead.model_validate(prestacion) for prestacion in prestaciones]


@router.post("", status_code=201, response_model=PrestacionRead)
def crear_prestacion(
    payload: PrestacionCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_role(RolUsuario.ADMIN)),
) -> PrestacionRead:
    try:
        prestacion = prestacion_service.crear(db, payload)
    except PrestacionRechazadaError as error:
        raise HTTPException(status_code=400, detail=error.motivo) from error
    return PrestacionRead.model_validate(prestacion)


@router.put("/{id}", response_model=PrestacionRead)
def editar_prestacion(
    id: int,
    payload: PrestacionUpdate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_role(RolUsuario.ADMIN)),
) -> PrestacionRead:
    try:
        prestacion = prestacion_service.actualizar(db, id, payload)
    except PrestacionNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=error.motivo) from error
    except PrestacionRechazadaError as error:
        raise HTTPException(status_code=400, detail=error.motivo) from error
    return PrestacionRead.model_validate(prestacion)
