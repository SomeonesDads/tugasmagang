"""Runtime configuration for the Telegram bot."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api").rstrip("/")
ENGINEER_DISTRICT = os.getenv("ENGINEER_DISTRICT")


def validate_config():
    missing = [name for name, value in {
        "TELEGRAM_BOT_TOKEN": TOKEN,
        "ENGINEER_DISTRICT": ENGINEER_DISTRICT,
    }.items() if not value]
    if missing:
        raise RuntimeError("Missing required environment variable(s): " + ", ".join(missing))
