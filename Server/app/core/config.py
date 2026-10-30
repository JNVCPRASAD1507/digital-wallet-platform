from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    secret_key: str = "change-me"
    database_url: str  
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    default_currency: str = "INR"
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings(): return Settings()
settings = get_settings()
