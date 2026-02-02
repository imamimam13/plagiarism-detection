from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Optional: External AI Detection APIs
    OPENAI_API_KEY: Optional[str] = ""  # For GPT-based AI detection
    ZEROGPT_API_KEY: Optional[str] = ""  # For ZeroGPT API
    COPYLEAKS_API_KEY: Optional[str]  = ""  # For CopyLeaks plagiarism API
    
    # Optional: Use external APIs instead of local models
    USE_EXTERNAL_AI_DETECTION: bool = False

    # AI Provider Support
    AI_PROVIDER: str = "openai" # openai, openrouter, ollama
    OPENROUTER_API_KEY: Optional[str] = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    
    # Plagiarism & Credit System
    SEARXNG_URL: str = "http://localhost:8080"
    ADMIN_WHATSAPP_NUMBER: str = "6285226462973" # Default placeholder
    SCAN_COST: int = 1

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
