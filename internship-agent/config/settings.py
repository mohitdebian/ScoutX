from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    provider_name: str = "tokenrouter"
    default_model: str = "kimi-k3"
    kimi_api_key: Optional[str] = None

    concurrency_limit: int = 5
    max_requests_per_minute: int = 60
    timeout_seconds: int = 30

    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    database_url: str = "sqlite+aiosqlite:///internships.db"

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Settings()
