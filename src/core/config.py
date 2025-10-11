from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Atlas"
    API_V1_PREFIX: str = "/api/v1"
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "atlas"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Admin
    ADMIN_SECRET_KEY: str
    
    # CORS
    CORS_ORIGINS: list = [
        "https://atlas.btreedevs.com.br",
        "https://btreedevs.com.br",
    ]
    ROOT_PATH: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
