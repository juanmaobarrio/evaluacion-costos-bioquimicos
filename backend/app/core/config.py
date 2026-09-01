from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema de Costos Bioquímicos"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Base de Datos: por defecto SQLite async para dev local sin requerir Postgres local inmediato, pero 100% compatible con Postgres
    DATABASE_URL: str = "sqlite+aiosqlite:///./costos_bioquimica.db"

    # Seguridad y JWT
    SECRET_KEY: str = "super_secret_costos_bioquimica_key_change_in_production_2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 horas

    # Moneda base y tasa de cambio por defecto
    DEFAULT_CURRENCY: str = "ARS"
    USD_EXCHANGE_RATE: float = 1200.0

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://localhost:3000"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
