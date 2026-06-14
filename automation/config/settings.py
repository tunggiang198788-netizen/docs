from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


@dataclass(frozen=True)
class Settings:
    apify_api_token: str
    apify_actor_id: str
    google_service_account_json: str
    gemini_api_key: str
    gemini_model: str
    google_drive_parent_folder_id: str
    slack_webhook_url: str
    telegram_bot_token: str
    telegram_chat_id: str


def load() -> Settings:
    required = {
        "APIFY_API_TOKEN": os.getenv("APIFY_API_TOKEN", ""),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "GOOGLE_SERVICE_ACCOUNT_JSON": os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", ""),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Copy automation/.env.example to automation/.env and fill in the values."
        )

    return Settings(
        apify_api_token=required["APIFY_API_TOKEN"],
        apify_actor_id=os.getenv("APIFY_TIKTOK_ACTOR_ID", "clockworks/tiktok-scraper"),
        google_service_account_json=required["GOOGLE_SERVICE_ACCOUNT_JSON"],
        gemini_api_key=required["GEMINI_API_KEY"],
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
        google_drive_parent_folder_id=os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", ""),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )
