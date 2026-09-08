from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Medical Appointment API"
    app_version: str = "1.0.0"
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

#Note:
#This lets us configure the application through environment variables later in Kubernetes:

#APP_NAME
#APP_VERSION
#ENVIRONMENT