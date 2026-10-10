class TurnoRechazadoError(Exception):
    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(motivo)


class TurnoSolapadoError(Exception):
    _MENSAJES = {
        "profesional": "Ya existe un turno del mismo profesional en ese horario.",
        "sillón": "El sillón ya está ocupado por otro profesional en ese horario.",
        "bloqueo": "El profesional tiene un bloqueo de agenda en ese horario.",
    }

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(self._MENSAJES.get(motivo, "Solapamiento de agenda."))
