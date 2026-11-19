from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.errores import (
    AccesoDenegadoError,
    CredencialesInvalidasError,
    ErrorAuth,
    IntentosExcedidosError,
    TokenInvalidoError,
    UsuarioRechazadoError,
)


def registrar_manejadores_auth(aplicacion: FastAPI) -> None:
    """Mapea errores de auth a respuestas HTTP sin lógica en los handlers."""

    @aplicacion.exception_handler(CredencialesInvalidasError)
    def _credenciales(
        _request: Request, error: CredencialesInvalidasError
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detalle": str(error)})

    @aplicacion.exception_handler(TokenInvalidoError)
    def _token_invalido(_request: Request, error: TokenInvalidoError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detalle": error.motivo})

    @aplicacion.exception_handler(AccesoDenegadoError)
    def _acceso_denegado(_request: Request, error: AccesoDenegadoError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detalle": str(error)})

    @aplicacion.exception_handler(IntentosExcedidosError)
    def _intentos_excedidos(
        _request: Request, error: IntentosExcedidosError
    ) -> JSONResponse:
        return JSONResponse(status_code=429, content={"detalle": str(error)})

    @aplicacion.exception_handler(UsuarioRechazadoError)
    def _usuario_rechazado(
        _request: Request, error: UsuarioRechazadoError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detalle": error.motivo})

    @aplicacion.exception_handler(ErrorAuth)
    def _error_auth(_request: Request, error: ErrorAuth) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detalle": str(error)})
