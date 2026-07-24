from __future__ import annotations

from clients.apify_client import VideoMeta, fetch_top_videos
from config.settings import Settings
from utils.logger import log


def run(settings: Settings, keyword: str, limit: int) -> list[VideoMeta]:
    log.info(f"[Step 1/6] Scraping top {limit} TikTok videos for '{keyword}'")
    videos = fetch_top_videos(
        api_token=settings.apify_api_token,
        actor_id=settings.apify_actor_id,
        keyword=keyword,
        limit=limit,
    )
    log.info(f"[Step 1/6] Done — {len(videos)} videos fetched")
    for v in videos[:5]:
        log.info(f"  Top {v.rank}: {v.view_count:,} views — {v.description[:60]}")
    return videos
