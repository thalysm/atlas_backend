from pydantic_settings import BaseSettings
from typing import List
import os, json


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
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    ROOT_PATH: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        value = os.getenv("CORS_ORIGINS", None)
        if value:
            try:
                # tenta decodificar como JSON
                return json.loads(value)
            except json.JSONDecodeError:
                # fallback: interpreta como CSV
                return [x.strip() for x in value.split(",") if x.strip()]
        return self.CORS_ORIGINS


settings = Settings()
