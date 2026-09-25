from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bharat Land Intelligence"
    ENVIRONMENT: str = "development"
    DEMO_MODE: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///../data/land_intelligence.db"
    
    # Auth
    SECRET_KEY: str = "generate_a_secure_random_key_here_for_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # AI Feature Flags
    ENABLE_PADDLE_OCR: bool = False
    ENABLE_SENTENCE_TRANSFORMERS: bool = False
    ENABLE_LOCAL_LLM: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
