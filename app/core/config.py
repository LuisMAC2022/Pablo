from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación.

    Los valores se cargan desde variables de entorno y, en desarrollo local,
    desde un archivo .env ubicado en la raíz del proyecto.
    """

    app_name: str = "Pablo"
    debug: bool = False

    database_url: str = Field(...)

    jwt_secret_key: SecretStr = Field(
        ...,
        validation_alias=AliasChoices("JWT_SECRET_KEY", "SECRET_KEY"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    visitantes_sheet_id: str = Field(..., min_length=1)
    password_temporal_biologos: SecretStr = Field(...)
    google_credentials_path: Path = Field(...)

    @field_validator("database_url")
    @classmethod
    def validar_database_url(cls, value: str) -> str:
        if "pabellon:pabellon123" in value:
            raise ValueError(
                "DATABASE_URL no debe usar credenciales de ejemplo "
                "como pabellon:pabellon123."
            )
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validar_jwt_secret_key(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if secret == "cambia_esto_por_una_clave_secreta_larga":
            raise ValueError("JWT_SECRET_KEY no debe usar el placeholder de ejemplo.")
        if len(secret) < 32:
            raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres.")
        return value

    @field_validator("password_temporal_biologos")
    @classmethod
    def validar_password_temporal_biologos(cls, value: SecretStr) -> SecretStr:
        if value.get_secret_value() == "biologo123":
            raise ValueError(
                "PASSWORD_TEMPORAL_BIOLOGOS no debe usar la contraseña de ejemplo."
            )
        return value

    @field_validator("google_credentials_path")
    @classmethod
    def validar_google_credentials_path(cls, value: Path) -> Path:
        if str(value).strip() in {"", "."}:
            raise ValueError("GOOGLE_CREDENTIALS_PATH debe apuntar a un archivo válido.")
        return value

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
