from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Sentinel AI"
    database_url: str = "postgresql+asyncpg://sentinel:sentinel@db:5432/sentinel"
    admin_token: str = "change-me"
    public_url: str = "http://localhost:8000"
    check_tick_seconds: int = 10
    incident_cooldown_minutes: int = 15
    llm_enabled: bool = True
    llm_base_url: str = "http://host.docker.internal:11434"
    llm_model: str = "qwen3.5:latest"
    llm_api_key: str = ""
    llm_timeout_seconds: int = 90
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    log_level: str = "INFO"

@lru_cache
def get_settings(): return Settings()
settings = get_settings()

