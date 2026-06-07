from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación.

    Los valores se cargan desde variables de entorno y, en desarrollo local,
    desde un archivo .env ubicado en la raíz del proyecto.
    """

    app_name: str = "Pablo"
    debug: bool = False

    database_url: str = (
        "postgresql://pabellon:pabellon123@localhost:5432/"
        "pabellon_db?client_encoding=utf8"
    )

    jwt_secret_key: str = Field(
        default="cambia_esto_por_una_clave_secreta_larga",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "SECRET_KEY"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    visitantes_sheet_id: str = ""
    password_temporal_biologos: str = "biologo123"
    google_credentials_path: Path = Path("credentials.json")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
