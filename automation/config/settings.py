from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


@dataclass(frozen=True)
class Settings:
    apify_api_token: str
    apify_actor_id: str
    gemini_api_key: str
    gemini_model: str
    google_service_account_json: str
    oauth_token_json: str
    user_email: str
    google_drive_parent_folder_id: str
    slack_webhook_url: str
    telegram_bot_token: str
    telegram_chat_id: str


def load() -> Settings:
    apify_token = os.getenv("APIFY_API_TOKEN", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if not apify_token:
        raise ValueError("Missing APIFY_API_TOKEN in .env")
    if not gemini_key:
        raise ValueError("Missing GEMINI_API_KEY in .env")

    sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    token_json = os.getenv("OAUTH_TOKEN_JSON", "token.json")

    has_oauth = token_json and Path(Path(__file__).parent.parent / token_json).exists()
    has_sa = sa_json and Path(sa_json).exists()

    if not has_oauth and not has_sa:
        raise ValueError(
            "No Google credentials found.\n"
            "Option 1 (personal Gmail): python setup_oauth.py\n"
            "Option 2 (Workspace): set GOOGLE_SERVICE_ACCOUNT_JSON in .env"
        )

    return Settings(
        apify_api_token=apify_token,
        apify_actor_id=os.getenv("APIFY_TIKTOK_ACTOR_ID", "clockworks/tiktok-scraper"),
        gemini_api_key=gemini_key,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        google_service_account_json=sa_json,
        oauth_token_json=str(Path(__file__).parent.parent / token_json) if token_json else "",
        user_email=os.getenv("USER_EMAIL", ""),
        google_drive_parent_folder_id=os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", ""),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )
