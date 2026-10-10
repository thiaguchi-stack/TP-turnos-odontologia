from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.turno import TurnoCreate, TurnoRead
from app.services.errores import TurnoRechazadoError, TurnoSolapadoError
from app.services.turno_service import crear_turno

router = APIRouter()


@router.post("/turnos", status_code=201, response_model=TurnoRead)
def crear_turnos(payload: TurnoCreate, db: Session = Depends(get_db)) -> TurnoRead:
    try:
        turno = crear_turno(
            db,
            profesional_id=payload.profesional_id,
            paciente_id=payload.paciente_id,
            prestacion_id=payload.prestacion_id,
            sillon_id=payload.sillon_id,
            fecha_hora_inicio=payload.fecha_hora_inicio,
        )
    except TurnoSolapadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except TurnoRechazadoError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return TurnoRead.model_validate(turno)
