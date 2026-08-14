"""Runtime configuration for the Telegram bot."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NODE_ENV = os.getenv("NODE_ENV", "development").strip().lower()
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api").rstrip("/")
DAILY_BROADCAST_TIME = os.getenv("DAILY_BROADCAST_TIME", "08:00")
DAILY_BROADCAST_TIMEZONE = os.getenv("DAILY_BROADCAST_TIMEZONE", "Asia/Jakarta")


def validate_config():
    if NODE_ENV == "prod":
        node_env = "production"
    else:
        node_env = NODE_ENV
    if node_env not in {"development", "staging", "production"}:
        raise RuntimeError("NODE_ENV must be development, staging, or production")

    missing = [name for name, value in {
        "TELEGRAM_BOT_TOKEN": TOKEN,
    }.items() if not value]
    if missing:
        raise RuntimeError("Missing required environment variable(s): " + ", ".join(missing))
