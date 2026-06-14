from __future__ import annotations

from pathlib import Path

from clients.drive_client import upload_all_videos
from config.settings import Settings
from pipeline.downloader import DownloadResult
from utils.logger import log


def run(settings: Settings, keyword: str, results: list[DownloadResult]) -> str:
    successful_paths = [r.local_path for r in results if r.success and r.local_path]
    log.info(f"[Step 4/6] Uploading {len(successful_paths)} videos to Google Drive")

    if not successful_paths:
        log.warning("[Step 4/6] No videos to upload, skipping")
        return ""

    folder_url, _ = upload_all_videos(
        service_account_json=settings.google_service_account_json,
        local_paths=successful_paths,
        keyword=keyword,
        parent_folder_id=settings.google_drive_parent_folder_id,
    )
    log.info(f"[Step 4/6] Done — {folder_url}")
    return folder_url
