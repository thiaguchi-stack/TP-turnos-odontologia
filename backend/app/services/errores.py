class ErrorAuth(Exception):
    """Error de autenticación o autorización con mensaje para la API."""


class TokenInvalidoError(ErrorAuth):
    def __init__(self, motivo: str = "Token inválido.") -> None:
        self.motivo = motivo
        super().__init__(motivo)


class TokenExpiradoError(TokenInvalidoError):
    def __init__(self) -> None:
        super().__init__("El token expiró.")


class CredencialesInvalidasError(ErrorAuth):
    def __init__(self) -> None:
        super().__init__("Usuario o contraseña incorrectos.")


class IntentosExcedidosError(ErrorAuth):
    def __init__(self) -> None:
        super().__init__("Demasiados intentos fallidos. Probá de nuevo más tarde.")


class AccesoDenegadoError(ErrorAuth):
    def __init__(self) -> None:
        super().__init__("No tenés permiso para realizar esta operación.")


class UsuarioRechazadoError(ErrorAuth):
    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(motivo)


class ProfesionalNoEncontradoError(Exception):
    def __init__(
        self, motivo: str = "No se encontró el profesional solicitado."
    ) -> None:
        self.motivo = motivo
        super().__init__(motivo)


class ProfesionalRechazadoError(Exception):
    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(motivo)


class PrestacionNoEncontradaError(Exception):
    def __init__(
        self, motivo: str = "No se encontró la prestación solicitada."
    ) -> None:
        self.motivo = motivo
        super().__init__(motivo)


class PrestacionRechazadaError(Exception):
    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(motivo)


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
