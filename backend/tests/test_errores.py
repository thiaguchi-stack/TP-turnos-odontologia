import pytest

from app.services.errores import (
    ErrorAuth,
    ProfesionalNoEncontradoError,
    ProfesionalRechazadoError,
    TurnoRechazadoError,
    TurnoSolapadoError,
)


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


def test_profesional_no_encontrado_expone_motivo_en_espanol():
    error = ProfesionalNoEncontradoError("No existe el profesional con id 12.")

    assert isinstance(error, Exception)
    assert error.motivo == "No existe el profesional con id 12."
    assert str(error) == "No existe el profesional con id 12."


def test_profesional_rechazado_expone_motivo_en_espanol():
    error = ProfesionalRechazadoError("El profesional está inactivo.")

    assert isinstance(error, Exception)
    assert error.motivo == "El profesional está inactivo."
    assert str(error) == "El profesional está inactivo."


def test_errores_de_profesional_no_son_de_auth_y_tienen_motivo_por_defecto():
    sin_encontrado = ProfesionalNoEncontradoError()

    assert sin_encontrado.motivo
    assert isinstance(sin_encontrado.motivo, str)
    assert not isinstance(sin_encontrado, ErrorAuth)
    assert not isinstance(ProfesionalRechazadoError("No permitido."), ErrorAuth)

    with pytest.raises(ProfesionalNoEncontradoError):
        raise ProfesionalNoEncontradoError("No existe el profesional con id 404.")

    with pytest.raises(ProfesionalRechazadoError):
        raise ProfesionalRechazadoError("El profesional no puede darse de baja.")
