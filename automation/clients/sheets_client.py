from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials

from utils.logger import log

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "STT", "Video ID", "URL", "Luot xem", "Luot thich",
    "Binh luan", "Mo ta", "Download URL", "Local Path", "Status",
]


def _get_client(service_account_json: str) -> gspread.Client:
    creds = Credentials.from_service_account_file(service_account_json, scopes=SCOPES)
    return gspread.authorize(creds)


def create_or_open_sheet(service_account_json: str, keyword: str) -> tuple[gspread.Spreadsheet, str]:
    gc = _get_client(service_account_json)
    title = f"{keyword} - Bang chi so tuong tac Top 30"

    try:
        spreadsheet = gc.open(title)
        log.info(f"[Sheets] Opened existing spreadsheet: {title}")
    except gspread.SpreadsheetNotFound:
        spreadsheet = gc.create(title)
        log.info(f"[Sheets] Created new spreadsheet: {title}")

    return spreadsheet, spreadsheet.url


def write_video_metadata(
    service_account_json: str,
    keyword: str,
    videos: list,
    local_paths: dict[int, str] | None = None,
) -> str:
    spreadsheet, url = create_or_open_sheet(service_account_json, keyword)
    ws = spreadsheet.sheet1
    ws.clear()
    ws.append_row(HEADERS)

    rows = []
    for v in videos:
        local = (local_paths or {}).get(v.rank, "")
        rows.append([
            v.rank,
            v.video_id,
            v.url,
            v.view_count,
            v.like_count,
            v.comment_count,
            v.description[:200],
            v.download_url,
            local,
            "downloaded" if local else "pending",
        ])

    if rows:
        ws.append_rows(rows)

    log.info(f"[Sheets] Wrote {len(rows)} rows → {url}")
    return url
