"""Environment-driven settings: API keys, DB URL, model name, CORS origins."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./app.db"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    weather_api_base_url: str = "https://api.open-meteo.com/v1/forecast"
    weather_geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"

    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "agrisense_knowledge"

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # bdapps CaaS (Charging as a Service) — set both to enable real sandbox
    # calls to developer.bdapps.com; leave blank to use the local in-process
    # simulator (see app/integrations/bdapps_caas.py). Never hardcode these —
    # only ever read from environment/.env.
    bdapps_application_id: str = ""
    bdapps_password: str = ""
    bdapps_caas_base_url: str = "https://developer.bdapps.com/caas"


@lru_cache
def get_settings() -> Settings:
    return Settings()
