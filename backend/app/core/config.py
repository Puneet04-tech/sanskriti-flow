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
    BACKEND_URL: str = "http://localhost:8000"

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
    WHISPER_MODEL: str = "base"  # Fast model with good accuracy (10x faster than large-v3)
    NLLB_MODEL: str = "facebook/nllb-200-distilled-600M"  # Higher quality translation model
    LLAMA_MODEL: str = "models/llama-3.1-8b-instruct.gguf"
    MOONDREAM_MODEL: str = "vikhyatk/moondream2"
    MODEL_DIR: str = "./models"  # Directory for ML model weights

    # Processing - Use absolute D drive paths to prevent C drive caching
    MAX_VIDEO_SIZE_MB: int = 500
    TEMP_DIR: str = "d:\\sanskriti-flow\\backend\\data\\temp"
    OUTPUT_DIR: str = "d:\\sanskriti-flow\\backend\\data\\output"
    CACHE_DIR: str = "d:\\sanskriti-flow\\backend\\data\\cache"
    TMP_DIR: str = "d:\\sanskriti-flow\\backend\\data\\cache\\tmp"

    # External cache directories (ABSOLUTE D drive paths - NO C drive fallback)
    HF_HOME: str = "d:\\sanskriti-flow\\backend\\data\\cache\\huggingface"
    TRANSFORMERS_CACHE: str = "d:\\sanskriti-flow\\backend\\data\\cache\\huggingface\\transformers"
    TORCH_HOME: str = "d:\\sanskriti-flow\\backend\\data\\cache\\torch"
    XDG_CACHE_HOME: str = "d:\\sanskriti-flow\\backend\\data\\cache"

    # Feature Flags
    ENABLE_VISION_SYNC: bool = True
    ENABLE_LIP_SYNC: bool = True
    ENABLE_QUIZ_GEN: bool = True
    ENABLE_SWAR: bool = True
    ENABLE_DRISHTI: bool = True

    # GPU
    CUDA_VISIBLE_DEVICES: str = "0"
    USE_GPU: bool = False  # Set to False if CUDA drivers not available

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Use absolute paths directly (no relative resolution needed)
temp_dir_abs = settings.TEMP_DIR
output_dir_abs = settings.OUTPUT_DIR
cache_dir_abs = settings.CACHE_DIR
tmp_dir_abs = settings.TMP_DIR
hf_home_abs = settings.HF_HOME
transformers_cache_abs = settings.TRANSFORMERS_CACHE
torch_home_abs = settings.TORCH_HOME
xdg_cache_home_abs = settings.XDG_CACHE_HOME

# FORCE ALL PYTHON/ML CACHES TO D DRIVE - Remove any C drive defaults
# This prevents models downloading to C:\Users\{user}\.cache
os.environ["HF_HOME"] = hf_home_abs
os.environ["TRANSFORMERS_CACHE"] = transformers_cache_abs
os.environ["TORCH_HOME"] = torch_home_abs
os.environ["XDG_CACHE_HOME"] = xdg_cache_home_abs
os.environ["TMPDIR"] = tmp_dir_abs
os.environ["TEMP"] = tmp_dir_abs
os.environ["TMP"] = tmp_dir_abs
# Also set PyTorch-specific caches
os.environ["PYTORCH_MPS_FALLBACK"] = "1"
# Prevent pip from caching on C drive
os.environ["PIP_CACHE_DIR"] = os.path.join(cache_dir_abs, "pip")
# Force matplotlib to use D drive for mplconfigdir
os.environ["MPLCONFIGDIR"] = os.path.join(cache_dir_abs, "matplotlib")

# Create all required directories on D drive
directories_to_create = [
    temp_dir_abs,
    output_dir_abs,
    cache_dir_abs,
    tmp_dir_abs,
    hf_home_abs,
    transformers_cache_abs,
    torch_home_abs,
    os.path.join(cache_dir_abs, "pip"),
    os.path.join(cache_dir_abs, "matplotlib"),
]

for dir_path in directories_to_create:
    os.makedirs(dir_path, exist_ok=True)

print(f"✅ Cache Configuration:")
print(f"   HF_HOME: {os.environ['HF_HOME']}")
print(f"   TORCH_HOME: {os.environ['TORCH_HOME']}")
print(f"   TEMP/TMP/TMPDIR: {os.environ['TMP']}")
print(f"   All caches configured to D drive")
