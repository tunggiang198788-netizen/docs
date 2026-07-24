from __future__ import annotations

from dataclasses import dataclass

from apify_client import ApifyClient
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import log


@dataclass
class VideoMeta:
    rank: int
    video_id: str
    url: str
    view_count: int
    like_count: int
    comment_count: int
    description: str
    download_url: str


def _extract_download_url(item: dict) -> str:
    video_meta = item.get("videoMeta", {})
    if isinstance(video_meta, dict):
        for field in ("downloadAddr", "originalDownloadAddr"):
            url = video_meta.get(field)
            if url:
                return url
    for field in ("videoUrl", "downloadUrl"):
        url = item.get(field)
        if url:
            return url
    return ""


def _extract_view_count(item: dict) -> int:
    for field in ("playCount", "viewCount", "plays"):
        val = item.get(field)
        if val is not None:
            return int(val)
    return 0


def _extract_video_id(item: dict) -> str:
    for field in ("id", "videoId", "aweme_id"):
        val = item.get(field)
        if val:
            return str(val)
    return item.get("webVideoUrl", "")[-19:] or "unknown"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=16))
def fetch_top_videos(api_token: str, actor_id: str, keyword: str, limit: int) -> list[VideoMeta]:
    log.info(f"[Apify] Scraping TikTok for keyword='{keyword}' limit={limit} actor={actor_id}")
    client = ApifyClient(api_token)

    run_input: dict = {
        "searchQueries": [keyword],
        "resultsPerPage": limit,
    }

    actor_call = client.actor(actor_id).call(run_input=run_input)
    dataset_id = actor_call["defaultDatasetId"]

    raw_items = list(client.dataset(dataset_id).iterate_items())
    log.info(f"[Apify] Fetched {len(raw_items)} raw items")

    videos: list[VideoMeta] = []
    for item in raw_items:
        download_url = _extract_download_url(item)
        if not download_url:
            log.warning(f"[Apify] No download URL for item, skipping")
            continue
        videos.append(
            VideoMeta(
                rank=0,
                video_id=_extract_video_id(item),
                url=item.get("webVideoUrl", item.get("url", "")),
                view_count=_extract_view_count(item),
                like_count=int(item.get("diggCount", item.get("likeCount", 0))),
                comment_count=int(item.get("commentCount", item.get("comments", 0))),
                description=item.get("text", item.get("desc", item.get("description", ""))),
                download_url=download_url,
            )
        )

    videos.sort(key=lambda v: v.view_count, reverse=True)
    videos = videos[:limit]
    for i, v in enumerate(videos):
        videos[i] = VideoMeta(
            rank=i + 1,
            video_id=v.video_id,
            url=v.url,
            view_count=v.view_count,
            like_count=v.like_count,
            comment_count=v.comment_count,
            description=v.description,
            download_url=v.download_url,
        )

    log.info(f"[Apify] Returning {len(videos)} videos sorted by view count")
    return videos
