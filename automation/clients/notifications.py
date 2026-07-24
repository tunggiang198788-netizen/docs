from __future__ import annotations

import requests

from utils.logger import log


def _slack(webhook_url: str, text: str) -> None:
    if not webhook_url:
        return
    try:
        r = requests.post(webhook_url, json={"text": text}, timeout=10)
        r.raise_for_status()
        log.info("[Notify] Slack alert sent")
    except Exception as e:
        log.warning(f"[Notify] Slack failed: {e}")


def _telegram(bot_token: str, chat_id: str, text: str) -> None:
    if not bot_token or not chat_id:
        return
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
        r.raise_for_status()
        log.info("[Notify] Telegram alert sent")
    except Exception as e:
        log.warning(f"[Notify] Telegram failed: {e}")


def send_success(
    keyword: str,
    sheet_url: str,
    drive_url: str,
    doc_url: str,
    slack_webhook: str,
    telegram_token: str,
    telegram_chat: str,
) -> None:
    msg = (
        f"✅ SOP Video Research HOÀN THÀNH\n"
        f"Keyword: {keyword}\n"
        f"📊 Google Sheet: {sheet_url}\n"
        f"🎬 Google Drive: {drive_url}\n"
        f"📄 Google Doc (Kế hoạch content): {doc_url}"
    )
    _slack(slack_webhook, msg)
    _telegram(telegram_token, telegram_chat, msg.replace("✅", "").replace("📊", "").replace("🎬", "").replace("📄", ""))


def send_failure(
    keyword: str,
    error: str,
    slack_webhook: str,
    telegram_token: str,
    telegram_chat: str,
) -> None:
    msg = f"❌ SOP Video Research THẤT BẠI\nKeyword: {keyword}\nLỗi: {error}"
    _slack(slack_webhook, msg)
    _telegram(telegram_token, telegram_chat, msg.replace("❌", "ERROR: "))
