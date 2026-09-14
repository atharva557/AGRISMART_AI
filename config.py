"""Application configuration. Keep real credentials in the local .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MODEL_WEIGHTS_PATH = os.getenv("MODEL_WEIGHTS_PATH", str(BASE_DIR / "model" / "weights"))
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    ASSISTANT_API_KEY = os.getenv("ASSISTANT_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("ASSISTANT_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
