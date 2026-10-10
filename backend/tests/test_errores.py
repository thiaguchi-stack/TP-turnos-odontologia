import pytest

from app.services.errores import TurnoRechazadoError, TurnoSolapadoError


def test_turno_rechazado_exponer_motivo_en_espanol():
    error = TurnoRechazadoError("El profesional está inactivo.")
    assert error.motivo == "El profesional está inactivo."
    assert str(error) == "El profesional está inactivo."


def test_turno_solapado_exponer_motivo_en_espanol():
    error = TurnoSolapadoError("profesional")
    assert error.motivo == "profesional"
    assert "profesional" in str(error)

    error_sillon = TurnoSolapadoError("sillón")
    assert error_sillon.motivo == "sillón"
    assert "sillón" in str(error_sillon)

    error_bloqueo = TurnoSolapadoError("bloqueo")
    assert error_bloqueo.motivo == "bloqueo"
    assert "bloqueo" in str(error_bloqueo)


def test_ambas_excepciones_se_levantan_con_pytest_raises():
    with pytest.raises(TurnoRechazadoError):
        raise TurnoRechazadoError("La prestación está inactiva.")

    with pytest.raises(TurnoSolapadoError):
        raise TurnoSolapadoError("bloqueo")
