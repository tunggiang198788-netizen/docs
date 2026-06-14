from __future__ import annotations

from clients.apify_client import VideoMeta
from clients.sheets_client import write_video_metadata
from config.settings import Settings
from utils.logger import log


def run(
    settings: Settings,
    keyword: str,
    videos: list[VideoMeta],
    local_paths: dict[int, str] | None = None,
) -> str:
    log.info(f"[Step 2/6] Logging {len(videos)} videos to Google Sheets")
    url = write_video_metadata(
        settings=settings,
        keyword=keyword,
        videos=videos,
        local_paths=local_paths,
    )
    log.info(f"[Step 2/6] Done — {url}")
    return url
