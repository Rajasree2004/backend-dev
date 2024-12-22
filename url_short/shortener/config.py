from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class Settings(BaseSettings):
    env_name : str = os.getenv('ENV_NAME')
    base_url : str = os.getenv('BASE_URL')
    db_url   : str = os.getenv('DB_URL')

    class Config:
        env_file = ".env"

@lru_cache #make it fast
def get_settings() -> Settings:
    setting = Settings()
    print(f"Load settings for: {setting.env_name}")
    return setting