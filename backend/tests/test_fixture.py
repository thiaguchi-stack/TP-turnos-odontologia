from sqlalchemy import select

from app.models import Bloqueo, Paciente, Prestacion, Profesional, Sillon, Turno


def test_fixture_seeds_datos_ficticios_en_cada_tabla(db, datos):
    assert len(db.scalars(select(Profesional)).all()) == 2
    assert len(db.scalars(select(Sillon)).all()) == 3
    assert len(db.scalars(select(Prestacion)).all()) == 3
    assert len(db.scalars(select(Paciente)).all()) == 1

    assert len(db.scalars(select(Turno)).all()) == 0
    assert len(db.scalars(select(Bloqueo)).all()) == 0

    assert datos.prof_activo.activo is True
    assert datos.prof_inactivo.activo is False
    assert datos.sillon_inactivo.activo is False
    assert datos.prestacion_inactiva.activa is False


def test_fixture_client_provee_testclient(db, client):
    respuesta = client.get("/api/health")
    assert respuesta.status_code == 200
