from __future__ import annotations

from pathlib import Path

from clients import gemini_client
from config.settings import Settings
from pipeline.downloader import DownloadResult
from prompts.master_prompt import get_preliminary_prompt, get_synthesis_prompt
from utils.logger import log

BATCH_SIZE = 10


def _upload_and_wait(local_paths: list[Path]) -> list[str]:
    active_names: list[str] = []
    for path in local_paths:
        name = gemini_client.upload_video(path)
        if not name:
            continue
        ok = gemini_client.wait_for_active(name)
        if ok:
            active_names.append(name)
        else:
            log.warning(f"[Analyzer] Skipping {path.name} (not ACTIVE)")
    return active_names


def _cleanup(names: list[str]) -> None:
    for name in names:
        gemini_client.delete_file(name)


def run(
    settings: Settings,
    keyword: str,
    results: list[DownloadResult],
    dry_run: bool = False,
) -> str:
    successful = [r for r in results if r.success and r.local_path]
    total = len(successful)

    if dry_run:
        estimate = gemini_client.estimate_cost(total, settings.gemini_model)
        log.info("[Step 5/6] DRY RUN — skipping Gemini analysis")
        log.info(
            f"[Step 5/6] Cost estimate: {estimate['num_videos']} videos x "
            f"~{estimate['tokens_per_video']:,} tokens/video x "
            f"~{estimate['estimated_input_tokens']:,} total tokens -> "
            f"~${estimate['estimated_cost_usd']:.4f} USD "
            f"(model: {settings.gemini_model})"
        )
        return "[DRY RUN — no analysis performed]"

    if not successful:
        log.warning("[Step 5/6] No videos available for analysis")
        return "[No videos available]"

    log.info(f"[Step 5/6] Analyzing {total} videos with Gemini ({settings.gemini_model})")
    gemini_client.configure(settings.gemini_api_key)

    all_paths = [r.local_path for r in successful]
    batches = [all_paths[i:i + BATCH_SIZE] for i in range(0, len(all_paths), BATCH_SIZE)]

    all_names: list[str] = []
    batch_names: list[list[str]] = []

    for i, batch_paths in enumerate(batches):
        log.info(f"[Step 5/6] Uploading batch {i+1}/{len(batches)} ({len(batch_paths)} videos)...")
        names = _upload_and_wait(batch_paths)
        batch_names.append(names)
        all_names.extend(names)

    try:
        preliminary_notes: list[str] = []
        for i, (names, batch_paths) in enumerate(zip(batch_names, batches)):
            if not names:
                preliminary_notes.append(f"[Batch {i+1} had no uploadable videos]")
                continue
            start = i * BATCH_SIZE + 1
            end = start + len(batch_paths) - 1
            prompt = get_preliminary_prompt(
                keyword=keyword, count=len(names), start=start, end=end, total=total
            )
            log.info(f"[Step 5/6] Preliminary analysis batch {i+1}/{len(batches)}...")
            notes = gemini_client.analyze_batch(settings.gemini_model, names, prompt)
            preliminary_notes.append(notes)
            log.info(f"[Step 5/6] Batch {i+1} notes: {len(notes)} chars")

        while len(preliminary_notes) < 3:
            preliminary_notes.append("[No data for this batch]")

        log.info("[Step 5/6] Running synthesis analysis...")
        synthesis_prompt = get_synthesis_prompt(
            keyword=keyword,
            total=total,
            notes_1=preliminary_notes[0],
            notes_2=preliminary_notes[1] if len(preliminary_notes) > 1 else "",
            notes_3=preliminary_notes[2] if len(preliminary_notes) > 2 else "",
        )
        final_analysis = gemini_client.analyze_batch(settings.gemini_model, [], synthesis_prompt)
        log.info(f"[Step 5/6] Done — {len(final_analysis)} chars of analysis")
        return final_analysis

    finally:
        _cleanup(all_names)
