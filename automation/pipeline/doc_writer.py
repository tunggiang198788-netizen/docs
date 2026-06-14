from __future__ import annotations

from clients.docs_client import write_analysis
from config.settings import Settings
from utils.logger import log


def run(settings: Settings, keyword: str, analysis_text: str) -> str:
    log.info("[Step 6/6] Writing analysis to Google Docs")

    if not analysis_text or analysis_text.startswith("["):
        log.warning("[Step 6/6] No analysis to write, skipping")
        return ""

    url = write_analysis(
        settings=settings,
        keyword=keyword,
        analysis_text=analysis_text,
    )
    log.info(f"[Step 6/6] Done — {url}")
    return url
