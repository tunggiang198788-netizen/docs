#!/usr/bin/env python3
"""
One-time OAuth2 consent flow for personal Gmail users.
Run once: python setup_oauth.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("ERROR: pip install google-auth-oauthlib")
        sys.exit(1)

    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/documents",
    ]

    client_secret = Path(__file__).parent / "client_secret.json"
    if not client_secret.exists():
        print("ERROR: client_secret.json not found in automation/")
        print()
        print("Setup steps:")
        print("1. Go to console.cloud.google.com -> APIs & Services -> Credentials")
        print("2. Create OAuth 2.0 Client ID (type: Desktop app)")
        print("3. Download JSON -> save as automation/client_secret.json")
        print("4. Enable APIs: Drive, Sheets, Docs")
        print("5. Add your Gmail to Test Users (OAuth consent screen)")
        print("6. Re-run: python setup_oauth.py")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), scopes)
    creds = flow.run_local_server(port=0)

    token_path = Path(__file__).parent / "token.json"
    token_path.write_text(creds.to_json())
    print(f"Done — credentials saved to {token_path}")
    print("You can now run: python run.py --keyword 'kem tri mun' --limit 3")


if __name__ == "__main__":
    main()
