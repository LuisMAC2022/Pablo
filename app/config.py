"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the application."""

    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    google_credentials_file: str = "credentials.json"
    solicitudes_spreadsheet_id: str
    visitantes_spreadsheet_id: str
    password_temporal_biologos: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        """Reject empty or placeholder secret keys."""
        if not value or not value.strip():
            raise ValueError("secret_key no puede estar vacío")

        if value == "cambia_esto_por_una_clave_secreta_larga":
            raise ValueError("secret_key debe cambiarse por una clave secreta segura")

        return value

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_access_token_expire_minutes(cls, value: int) -> int:
        """Ensure access tokens have a positive expiration time."""
        if value <= 0:
            raise ValueError("access_token_expire_minutes debe ser mayor que 0")

        return value

    @field_validator("solicitudes_spreadsheet_id", "visitantes_spreadsheet_id")
    @classmethod
    def validate_google_sheet_id(cls, value: str) -> str:
        """Reject empty Google Sheets identifiers."""
        if not value or not value.strip():
            raise ValueError("Los IDs de Google Sheets no pueden estar vacíos")

        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
