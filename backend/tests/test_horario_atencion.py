from datetime import time

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import HorarioAtencion, Profesional

NUEVE = time(9, 0)
TRECE = time(13, 0)
OCHO = time(8, 0)


@pytest.fixture(autouse=True)
def _esquema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _profesional(db) -> int:
    prof = Profesional(nombre="Ana", apellido="Rivas", especialidad="Ortodoncia")
    db.add(prof)
    db.commit()
    return prof.id


def test_horario_atencion_franja_valida_se_persiste():
    with SessionLocal() as db:
        profesional_id = _profesional(db)
        ha = HorarioAtencion(
            profesional_id=profesional_id,
            dia_semana=0,  # lunes
            hora_inicio=NUEVE,
            hora_fin=TRECE,
        )
        db.add(ha)
        db.commit()
        db.refresh(ha)

    assert ha.id is not None
    assert ha.dia_semana == 0
    assert ha.profesional_id == profesional_id


def test_horario_atencion_hora_fin_menor_igual_inicio_rechazada():
    with SessionLocal() as db:
        profesional_id = _profesional(db)
        ha = HorarioAtencion(
            profesional_id=profesional_id,
            dia_semana=1,
            hora_inicio=TRECE,
            hora_fin=NUEVE,
        )
        db.add(ha)
        with pytest.raises(IntegrityError):
            db.commit()


def test_horario_atencion_hora_fin_igual_inicio_rechazada():
    with SessionLocal() as db:
        profesional_id = _profesional(db)
        ha = HorarioAtencion(
            profesional_id=profesional_id,
            dia_semana=2,
            hora_inicio=NUEVE,
            hora_fin=NUEVE,
        )
        db.add(ha)
        with pytest.raises(IntegrityError):
            db.commit()


def test_horario_atencion_fk_profesional_inexistente_rechazada():
    with SessionLocal() as db:
        ha = HorarioAtencion(
            profesional_id=999,
            dia_semana=0,
            hora_inicio=NUEVE,
            hora_fin=TRECE,
        )
        db.add(ha)
        with pytest.raises(IntegrityError):
            db.commit()


def test_horario_atencion_dos_franjas_mismo_dia_mismo_profesional_conviven():
    with SessionLocal() as db:
        profesional_id = _profesional(db)
        manana = HorarioAtencion(
            profesional_id=profesional_id,
            dia_semana=0,
            hora_inicio=time(9, 0),
            hora_fin=time(13, 0),
        )
        tarde = HorarioAtencion(
            profesional_id=profesional_id,
            dia_semana=0,
            hora_inicio=time(15, 0),
            hora_fin=time(19, 0),
        )
        db.add_all([manana, tarde])
        db.commit()
        db.refresh(manana)
        db.refresh(tarde)

    assert manana.id is not None
    assert tarde.id is not None


def test_horario_atencion_franjas_superpuestas_son_permitidas_por_el_modelo():
    """TRIANGULATE (task 4.3): el modelo NO prohíbe franjas superpuestas.

    La unicidad es por ``(profesional_id, dia_semana, hora_inicio)`` y el único
    ``CHECK`` es ``hora_fin > hora_inicio``; por lo tanto dos franjas del mismo
    día con distinto horario de inicio pero solapadas conviven en la base.
    La detección/merge de superposiciones queda deliberadamente para `C-07`
    (agenda-engine), que consume `HorarioAtencion`; C-02 solo garantiza la
    integridad declarada en la spec. Este test captura esa decisión.
    """
    with SessionLocal() as db:
        profesional_id = _profesional(db)
        franja_a = HorarioAtencion(
            profesional_id=profesional_id,
            dia_semana=0,
            hora_inicio=time(9, 0),
            hora_fin=time(13, 0),
        )
        franja_b = HorarioAtencion(
            profesional_id=profesional_id,
            dia_semana=0,
            hora_inicio=time(12, 0),
            hora_fin=time(16, 0),
        )
        db.add_all([franja_a, franja_b])
        db.commit()
        db.refresh(franja_a)
        db.refresh(franja_b)

    assert franja_a.id is not None
    assert franja_b.id is not None
