import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORT_DIR = BASE_DIR / "reports_output"
SAMPLE_DIR = BASE_DIR / "sample_data"
DB_PATH = BASE_DIR / "signal_assistant.db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "NTRO Signal Analysis Assistant"
    PROJECT_ID: str = "26147"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    MAX_UPLOAD_SIZE_MB: int = 200
    DEFAULT_SAMPLE_RATE: float = 1000000.0  # 1 MSps default for IQ if unspecified
    
    class Config:
        case_sensitive = True

settings = Settings()
