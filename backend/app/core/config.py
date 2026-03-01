"""
Core Configuration Module
Loads environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sanskriti-Flow"
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Model Paths
    WHISPER_MODEL: str = "base"
    NLLB_MODEL: str = "facebook/nllb-200-distilled-600M"
    LLAMA_MODEL: str = "models/llama-3.1-8b-instruct.gguf"
    MOONDREAM_MODEL: str = "vikhyatk/moondream2"

    # Processing
    MAX_VIDEO_SIZE_MB: int = 500
    TEMP_DIR: str = "./data/temp"
    OUTPUT_DIR: str = "./data/output"
    CACHE_DIR: str = "./data/cache"

    # Feature Flags
    ENABLE_VISION_SYNC: bool = True
    ENABLE_LIP_SYNC: bool = True
    ENABLE_QUIZ_GEN: bool = True
    ENABLE_SWAR: bool = True
    ENABLE_DRISHTI: bool = True

    # GPU
    CUDA_VISIBLE_DEVICES: str = "0"
    USE_GPU: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure directories exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.CACHE_DIR, exist_ok=True)
