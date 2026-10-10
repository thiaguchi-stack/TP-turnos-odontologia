from datetime import datetime, timedelta

from sqlalchemy import select

from app.models import Bloqueo, Profesional, Turno


def _payload(datos, *, inicio="2026-11-05T09:00:00", **extra):
    payload = {
        "profesional_id": datos.prof_activo.id,
        "paciente_id": datos.paciente.id,
        "prestacion_id": datos.prestacion_30.id,
        "sillon_id": datos.sillon_1.id,
        "fecha_hora_inicio": inicio,
    }
    payload.update(extra)
    return payload


def test_creacion_feliz_responde_201_con_fin_derivado_y_reservado(client, datos):
    respuesta = client.post("/turnos", json=_payload(datos))

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "reservado"
    assert cuerpo["fecha_hora_inicio"] == "2026-11-05T09:00:00"
    assert cuerpo["fecha_hora_fin"] == "2026-11-05T09:30:00"
    assert cuerpo["sillon_id"] == datos.sillon_1.id
    assert cuerpo["id"] > 0


def test_solicitud_con_campos_prohibidos_responde_400(client, datos, db):
    payload = _payload(
        datos,
        fecha_hora_fin="2026-11-05T09:59:00",
        estado="confirmado",
    )

    respuesta = client.post("/turnos", json=payload)

    assert respuesta.status_code == 400
    assert "detail" in respuesta.json()

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 0


def test_409_colision_por_profesional_con_sillon_distinto(client, datos, db):
    creada = client.post("/turnos", json=_payload(datos, sillon_id=datos.sillon_1.id))
    assert creada.status_code == 201

    respuesta = client.post(
        "/turnos",
        json=_payload(datos, inicio="2026-11-05T09:15:00", sillon_id=datos.sillon_2.id),
    )

    assert respuesta.status_code == 409
    assert "profesional" in respuesta.json()["detail"].lower()

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 1


def test_409_colision_por_sillon_con_profesional_distinto(client, datos, db):
    segundo = Profesional(nombre="Carla", apellido="Méndez", especialidad="Cirugía")
    db.add(segundo)
    db.commit()
    segundo_id = segundo.id
    db.commit()

    creada = client.post("/turnos", json=_payload(datos, sillon_id=datos.sillon_1.id))
    assert creada.status_code == 201

    respuesta = client.post(
        "/turnos",
        json=_payload(datos, inicio="2026-11-05T09:20:00", profesional_id=segundo_id),
    )

    assert respuesta.status_code == 409
    assert "sillón" in respuesta.json()["detail"].lower()

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 1


def test_409_colision_con_bloqueo_del_profesional(client, datos, db):
    db.add(
        Bloqueo(
            profesional_id=datos.prof_activo.id,
            sillon_id=None,
            fecha_hora_inicio=datetime(2026, 11, 5, 15, 0),
            fecha_hora_fin=datetime(2026, 11, 5, 19, 0),
        )
    )
    db.commit()

    respuesta = client.post(
        "/turnos", json=_payload(datos, inicio="2026-11-05T16:00:00")
    )

    assert respuesta.status_code == 409
    assert "bloqueo" in respuesta.json()["detail"].lower()

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 0


def test_400_turno_en_el_pasado(client, datos, db):
    en_el_pasado = (datetime.now() - timedelta(hours=2)).isoformat(timespec="seconds")

    respuesta = client.post("/turnos", json=_payload(datos, inicio=en_el_pasado))

    assert respuesta.status_code == 400
    assert "pasado" in respuesta.json()["detail"].lower()

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 0


def test_400_profesional_inactivo(client, datos, db):
    respuesta = client.post(
        "/turnos", json=_payload(datos, profesional_id=datos.prof_inactivo.id)
    )

    assert respuesta.status_code == 400
    assert "inactivo" in respuesta.json()["detail"].lower()

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 0


def test_400_sillon_inactivo(client, datos, db):
    respuesta = client.post(
        "/turnos", json=_payload(datos, sillon_id=datos.sillon_inactivo.id)
    )

    assert respuesta.status_code == 400
    assert "sillón" in respuesta.json()["detail"].lower()

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 0


def test_400_prestacion_inactiva(client, datos, db):
    respuesta = client.post(
        "/turnos", json=_payload(datos, prestacion_id=datos.prestacion_inactiva.id)
    )

    assert respuesta.status_code == 400
    assert "prestación" in respuesta.json()["detail"].lower()

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 0


def test_201_borde_inicio_igual_al_fin_de_otro_turno(client, datos, db):
    primera = client.post("/turnos", json=_payload(datos, sillon_id=datos.sillon_1.id))
    assert primera.status_code == 201

    en_el_borde = client.post(
        "/turnos",
        json=_payload(datos, inicio="2026-11-05T09:30:00", sillon_id=datos.sillon_1.id),
    )

    assert en_el_borde.status_code == 201
    assert en_el_borde.json()["fecha_hora_fin"] == "2026-11-05T10:00:00"

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 2


def test_201_creacion_sobre_turno_cancelado(client, datos, db):
    creada = client.post("/turnos", json=_payload(datos, sillon_id=datos.sillon_1.id))
    assert creada.status_code == 201

    turno = db.get(Turno, creada.json()["id"])
    turno.estado = "cancelado"
    db.commit()

    sobre_cancelado = client.post(
        "/turnos",
        json=_payload(datos, inicio="2026-11-05T09:10:00", sillon_id=datos.sillon_1.id),
    )

    assert sobre_cancelado.status_code == 201
    assert sobre_cancelado.json()["estado"] == "reservado"

    db.expire_all()
    assert len(db.scalars(select(Turno)).all()) == 2
