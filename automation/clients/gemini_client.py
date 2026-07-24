from __future__ import annotations

import time
from pathlib import Path

from google import genai
from google.genai import types

from utils.logger import log

UPLOAD_TIMEOUT_SECONDS = 300
POLL_INTERVAL_SECONDS = 10
TOKENS_PER_SECOND = 300

_client: genai.Client | None = None


def configure(api_key: str) -> None:
    global _client
    _client = genai.Client(api_key=api_key)


def _get_client() -> genai.Client:
    if _client is None:
        raise RuntimeError("Call configure(api_key) first")
    return _client


def upload_video(local_path: Path) -> str | None:
    log.info(f"[Gemini] Uploading {local_path.name}...")
    try:
        client = _get_client()
        uploaded = client.files.upload(file=str(local_path))
        log.info(f"[Gemini] Uploaded -> name={uploaded.name} state={uploaded.state}")
        return uploaded.name
    except Exception as e:
        log.warning(f"[Gemini] Upload failed for {local_path.name}: {e}")
        return None


def wait_for_active(file_name: str, timeout: int = UPLOAD_TIMEOUT_SECONDS) -> bool:
    client = _get_client()
    elapsed = 0
    while elapsed < timeout:
        try:
            f = client.files.get(name=file_name)
            state = str(f.state)
            if "ACTIVE" in state:
                log.info(f"[Gemini] {file_name} is ACTIVE")
                return True
            if "FAILED" in state:
                log.warning(f"[Gemini] {file_name} FAILED to process")
                return False
            log.info(f"[Gemini] {file_name} state={state}, waiting...")
        except Exception as e:
            log.warning(f"[Gemini] Error polling {file_name}: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS

    log.warning(f"[Gemini] {file_name} timed out after {timeout}s")
    return False


def delete_file(file_name: str) -> None:
    try:
        client = _get_client()
        client.files.delete(name=file_name)
        log.info(f"[Gemini] Deleted {file_name}")
    except Exception as e:
        log.warning(f"[Gemini] Could not delete {file_name}: {e}")


def analyze_batch(
    model_name: str,
    file_names: list[str],
    prompt: str,
) -> str:
    client = _get_client()
    contents = []
    for name in file_names:
        f = client.files.get(name=name)
        contents.append(types.Part.from_uri(file_uri=f.uri, mime_type="video/mp4"))
    contents.append(prompt)

    log.info(f"[Gemini] Calling {model_name} with {len(file_names)} videos...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.4, top_p=0.95),
        )
        return response.text
    except Exception as e:
        log.error(f"[Gemini] generate_content failed: {e}")
        raise


def estimate_cost(num_videos: int, model_name: str, avg_duration_sec: int = 45) -> dict:
    tokens_per_video = TOKENS_PER_SECOND * avg_duration_sec
    total_tokens = tokens_per_video * num_videos
    prices = {
        "gemini-2.5-flash": 0.15,
        "gemini-2.5-pro": 1.25,
        "gemini-2.0-flash": 0.10,
    }
    price_per_million = prices.get(model_name, 0.15)
    cost_usd = (total_tokens / 1_000_000) * price_per_million
    return {
        "num_videos": num_videos,
        "avg_duration_sec": avg_duration_sec,
        "tokens_per_video": tokens_per_video,
        "estimated_input_tokens": total_tokens,
        "price_per_million_tokens_usd": price_per_million,
        "estimated_cost_usd": round(cost_usd, 4),
    }
