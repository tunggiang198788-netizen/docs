from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import requests
from tqdm import tqdm

from clients.apify_client import VideoMeta
from utils.filename import make_filename
from utils.logger import log


@dataclass
class DownloadResult:
    video: VideoMeta
    local_path: Path | None
    success: bool
    error: str | None


def _download_one(video: VideoMeta, output_dir: Path) -> DownloadResult:
    filename = make_filename(video.rank, video.view_count, video.description)
    dest = output_dir / filename

    if dest.exists():
        log.info(f"  [skip] {filename} already exists")
        return DownloadResult(video=video, local_path=dest, success=True, error=None)

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}
        with requests.get(video.download_url, stream=True, timeout=60, headers=headers) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with open(dest, "wb") as f, tqdm(
                total=total, unit="B", unit_scale=True, desc=filename[:40], leave=False
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))

        size_mb = dest.stat().st_size / 1024 / 1024
        log.info(f"  ✓ {filename} ({size_mb:.1f} MB)")
        return DownloadResult(video=video, local_path=dest, success=True, error=None)

    except Exception as e:
        if dest.exists():
            dest.unlink()
        log.warning(f"  ✗ {filename}: {e}")
        return DownloadResult(video=video, local_path=None, success=False, error=str(e))


def run(videos: list[VideoMeta], output_dir: Path) -> list[DownloadResult]:
    output_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"[Step 3/6] Downloading {len(videos)} videos to {output_dir}")

    results: list[DownloadResult] = []
    for video in videos:
        result = _download_one(video, output_dir)
        results.append(result)
        if result.success:
            time.sleep(1)

    ok = sum(1 for r in results if r.success)
    log.info(f"[Step 3/6] Done — {ok}/{len(videos)} downloaded successfully")
    return results
