from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./clinica.db"
    secret_key: str = "dev-insecure-cambiame-en-produccion"
    token_expire_min: int = 60
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parsear_cors_origins(cls, valor: object) -> object:
        """Normaliza CORS_ORIGINS: acepta lista o string separado por comas."""
        if isinstance(valor, str):
            return [origen.strip() for origen in valor.split(",") if origen.strip()]
        return valor


settings = Settings()
