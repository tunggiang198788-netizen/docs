from __future__ import annotations

import gspread

from clients.auth import get_credentials, is_service_account
from utils.logger import log

HEADERS = [
    "STT", "Video ID", "URL", "Luot xem", "Luot thich",
    "Binh luan", "Mo ta", "Download URL", "Local Path", "Status",
]


def _get_client(settings) -> gspread.Client:
    creds = get_credentials(settings)
    return gspread.authorize(creds)


def _share_if_needed(settings, spreadsheet: gspread.Spreadsheet) -> None:
    creds = get_credentials(settings)
    if not is_service_account(creds) or not settings.user_email:
        return
    spreadsheet.share(settings.user_email, perm_type="user", role="writer", notify=False)
    log.info(f"[Sheets] Shared with {settings.user_email}")


def create_or_open_sheet(settings, keyword: str) -> tuple[gspread.Spreadsheet, str]:
    gc = _get_client(settings)
    title = f"{keyword} - Bang chi so tuong tac Top 30"

    try:
        spreadsheet = gc.open(title)
        log.info(f"[Sheets] Opened existing spreadsheet: {title}")
    except gspread.SpreadsheetNotFound:
        spreadsheet = gc.create(title)
        _share_if_needed(settings, spreadsheet)
        log.info(f"[Sheets] Created new spreadsheet: {title}")

    return spreadsheet, spreadsheet.url


def write_video_metadata(
    settings,
    keyword: str,
    videos: list,
    local_paths: dict[int, str] | None = None,
) -> str:
    spreadsheet, url = create_or_open_sheet(settings, keyword)
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

    log.info(f"[Sheets] Wrote {len(rows)} rows -> {url}")
    return url
