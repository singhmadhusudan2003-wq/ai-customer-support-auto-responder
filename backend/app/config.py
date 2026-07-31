"""
config.py
---------
Central application configuration, loaded from environment variables
(via a .env file if present). Uses pydantic-settings for validation.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI Customer Support Auto-Responder"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- Security / JWT ---
    SECRET_KEY: str = "CHANGE_ME_SUPER_SECRET_KEY_IN_PRODUCTION_9f8a7d6c5b4a"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # --- Database ---
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'backend' / 'support.db'}"

    # --- CORS ---
    CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    "https://ai-customer-support-auto-responder.vercel.app",
    "https://ai-customer-support-auto-responder-git-main-singhmadhusudan2003-wq.vercel.app",
]

    # --- AI / Models ---
    MODELS_DIR: str = str(BASE_DIR / "models" / "saved")
    DATASET_DIR: str = str(BASE_DIR / "dataset")
    CONFIDENCE_ESCALATION_THRESHOLD: float = 0.45  # below this -> escalate to human

    # --- Optional external LLM providers ---
    OPENAI_API_KEY: str = ""
    USE_OPENAI: bool = False
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    USE_OLLAMA: bool = False

    # --- Default admin (auto-created on first run) ---
    DEFAULT_ADMIN_EMAIL: str = "admin@example.com"
    DEFAULT_ADMIN_PASSWORD: str = "Admin@123"
    DEFAULT_ADMIN_NAME: str = "Support Admin"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
