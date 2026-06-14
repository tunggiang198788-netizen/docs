from __future__ import annotations

from pathlib import Path

from google.oauth2.service_account import Credentials as SACredentials
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request

from utils.logger import log

ALL_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
]

_cached_creds = None


def get_credentials(settings) -> SACredentials | UserCredentials:
    global _cached_creds
    if _cached_creds is not None and _cached_creds.valid:
        return _cached_creds

    token_path = Path(settings.oauth_token_json) if settings.oauth_token_json else None
    if token_path and token_path.exists():
        creds = UserCredentials.from_authorized_user_file(str(token_path), ALL_SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
        if creds and creds.valid:
            log.info("[Auth] Using OAuth2 user credentials (personal Gmail)")
            _cached_creds = creds
            return creds

    sa_path = settings.google_service_account_json
    if sa_path and Path(sa_path).exists():
        log.info("[Auth] Using service account credentials")
        creds = SACredentials.from_service_account_file(sa_path, scopes=ALL_SCOPES)
        _cached_creds = creds
        return creds

    raise ValueError(
        "No valid Google credentials found.\n"
        "Option 1 (recommended for personal Gmail): python setup_oauth.py\n"
        "Option 2 (Google Workspace only): set GOOGLE_SERVICE_ACCOUNT_JSON in .env"
    )


def is_service_account(creds) -> bool:
    return isinstance(creds, SACredentials)
