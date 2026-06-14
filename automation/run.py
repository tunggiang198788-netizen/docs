#!/usr/bin/env python3
"""
Video Competitor Research Automation — SOP 2
Usage: python run.py --keyword "kem tri mun" --limit 30
"""
from __future__ import annotations

import argparse
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings as settings_module
from config.settings import Settings
from utils.logger import log

import pipeline.scraper as step_scraper
import pipeline.sheet_logger as step_sheets
import pipeline.downloader as step_downloader
import pipeline.uploader as step_uploader
import pipeline.analyzer as step_analyzer
import pipeline.doc_writer as step_doc

from clients import notifications


@dataclass
class RunContext:
    keyword: str
    limit: int
    dry_run: bool
    skip_download: bool
    skip_upload: bool
    output_dir: Path


def parse_args() -> RunContext:
    parser = argparse.ArgumentParser(
        description="TikTok competitor video research & content plan automation"
    )
    parser.add_argument("--keyword", required=True, help='Search keyword, e.g. "kem tri mun"')
    parser.add_argument("--limit", type=int, default=30, help="Number of top videos to analyze (default: 30)")
    parser.add_argument("--dry-run", action="store_true", help="Scrape + log Sheets only; skip download & Gemini")
    parser.add_argument("--skip-download", action="store_true", help="Reuse existing videos in output-dir")
    parser.add_argument("--skip-upload", action="store_true", help="Skip Google Drive upload")
    parser.add_argument("--output-dir", default="downloads", help="Local video storage path (default: downloads/)")
    args = parser.parse_args()

    return RunContext(
        keyword=args.keyword,
        limit=args.limit,
        dry_run=args.dry_run,
        skip_download=args.skip_download,
        skip_upload=args.skip_upload,
        output_dir=Path(__file__).parent / args.output_dir,
    )


def main() -> None:
    ctx = parse_args()

    log.info("=" * 60)
    log.info(f"SOP Video Research Automation")
    log.info(f"Keyword : {ctx.keyword}")
    log.info(f"Limit   : {ctx.limit} videos")
    log.info(f"Dry run : {ctx.dry_run}")
    log.info("=" * 60)

    settings: Settings = settings_module.load()

    sheet_url = ""
    drive_url = ""
    doc_url = ""

    try:
        videos = step_scraper.run(settings, ctx.keyword, ctx.limit)

        sheet_url = step_sheets.run(settings, ctx.keyword, videos)

        if ctx.dry_run:
            log.info("[DRY RUN] Stopping after Sheets log. Use without --dry-run for full run.")
            step_analyzer.run(settings, ctx.keyword, [], dry_run=True)
            notifications.send_success(
                ctx.keyword, sheet_url, "(skipped)", "(skipped)",
                settings.slack_webhook_url, settings.telegram_bot_token, settings.telegram_chat_id,
            )
            return

        if ctx.skip_download:
            log.info("[skip-download] Loading existing videos from disk...")
            from clients.apify_client import VideoMeta
            from pipeline.downloader import DownloadResult
            existing = sorted(ctx.output_dir.glob("Top_*.mp4"))
            download_results = []
            for path in existing:
                rank = int(path.name.split("_")[1])
                matching = next((v for v in videos if v.rank == rank), None)
                if matching:
                    download_results.append(
                        DownloadResult(video=matching, local_path=path, success=True, error=None)
                    )
            log.info(f"[skip-download] Found {len(download_results)} existing videos")
        else:
            download_results = step_downloader.run(videos, ctx.output_dir)

        local_paths_map = {
            r.video.rank: str(r.local_path)
            for r in download_results if r.success and r.local_path
        }
        step_sheets.run(settings, ctx.keyword, videos, local_paths=local_paths_map)

        if not ctx.skip_upload:
            drive_url = step_uploader.run(settings, ctx.keyword, download_results)
        else:
            log.info("[skip-upload] Skipping Google Drive upload")

        analysis = step_analyzer.run(settings, ctx.keyword, download_results, dry_run=False)

        doc_url = step_doc.run(settings, ctx.keyword, analysis)

        log.info("=" * 60)
        log.info("DONE")
        log.info(f"Google Sheet  : {sheet_url}")
        log.info(f"Google Drive  : {drive_url}")
        log.info(f"Google Doc    : {doc_url}")
        log.info("=" * 60)

        notifications.send_success(
            ctx.keyword, sheet_url, drive_url, doc_url,
            settings.slack_webhook_url, settings.telegram_bot_token, settings.telegram_chat_id,
        )

    except Exception as e:
        tb = traceback.format_exc()
        log.error(f"Pipeline failed: {e}\n{tb}")
        notifications.send_failure(
            ctx.keyword, str(e),
            settings.slack_webhook_url, settings.telegram_bot_token, settings.telegram_chat_id,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
