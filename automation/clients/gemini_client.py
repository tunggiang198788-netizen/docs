from __future__ import annotations

import time
from pathlib import Path

import google.generativeai as genai

from utils.logger import log

UPLOAD_TIMEOUT_SECONDS = 300
POLL_INTERVAL_SECONDS = 10


def configure(api_key: str) -> None:
    genai.configure(api_key=api_key)


def upload_video(local_path: Path) -> str | None:
    log.info(f"[Gemini] Uploading {local_path.name}...")
    try:
        file = genai.upload_file(path=str(local_path), mime_type="video/mp4")
        log.info(f"[Gemini] Uploaded → uri={file.uri} state={file.state.name}")
        return file.uri
    except Exception as e:
        log.warning(f"[Gemini] Upload failed for {local_path.name}: {e}")
        return None


def wait_for_active(file_uri: str, timeout: int = UPLOAD_TIMEOUT_SECONDS) -> bool:
    elapsed = 0
    file_name = file_uri.split("/")[-1]
    while elapsed < timeout:
        try:
            f = genai.get_file(file_name)
            state = f.state.name
            if state == "ACTIVE":
                log.info(f"[Gemini] {file_name} is ACTIVE")
                return True
            if state == "FAILED":
                log.warning(f"[Gemini] {file_name} FAILED to process")
                return False
            log.info(f"[Gemini] {file_name} state={state}, waiting...")
        except Exception as e:
            log.warning(f"[Gemini] Error polling {file_name}: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS

    log.warning(f"[Gemini] {file_name} timed out after {timeout}s")
    return False


def delete_file(file_uri: str) -> None:
    try:
        file_name = file_uri.split("/")[-1]
        genai.delete_file(file_name)
        log.info(f"[Gemini] Deleted {file_name}")
    except Exception as e:
        log.warning(f"[Gemini] Could not delete {file_uri}: {e}")


def analyze_batch(
    model_name: str,
    file_uris: list[str],
    prompt: str,
) -> str:
    model = genai.GenerativeModel(model_name)
    parts = []
    for uri in file_uris:
        parts.append({"file_data": {"mime_type": "video/mp4", "file_uri": uri}})
    parts.append(prompt)

    log.info(f"[Gemini] Calling {model_name} with {len(file_uris)} videos...")
    try:
        response = model.generate_content(parts, generation_config={"temperature": 0.4, "top_p": 0.95})
        return response.text
    except Exception as e:
        log.error(f"[Gemini] generate_content failed: {e}")
        raise


def estimate_cost(num_videos: int, model_name: str) -> dict:
    tokens_per_video = 300_000
    total_tokens = tokens_per_video * num_videos
    prices = {
        "gemini-1.5-pro": 3.50,
        "gemini-1.5-flash": 0.075,
        "gemini-2.0-flash": 0.10,
    }
    price_per_million = prices.get(model_name, 3.50)
    cost_usd = (total_tokens / 1_000_000) * price_per_million
    return {
        "num_videos": num_videos,
        "estimated_input_tokens": total_tokens,
        "price_per_million_tokens_usd": price_per_million,
        "estimated_cost_usd": round(cost_usd, 2),
    }
