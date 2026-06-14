from __future__ import annotations

from datetime import date

from googleapiclient.discovery import build

from clients.auth import get_credentials, is_service_account
from utils.logger import log


def _get_docs_service(settings):
    creds = get_credentials(settings)
    return build("docs", "v1", credentials=creds)


def _get_drive_service(settings):
    creds = get_credentials(settings)
    return build("drive", "v3", credentials=creds)


def _share_if_needed(settings, file_id: str) -> None:
    creds = get_credentials(settings)
    if not is_service_account(creds) or not settings.user_email:
        return
    service = build("drive", "v3", credentials=creds)
    service.permissions().create(
        fileId=file_id,
        body={"type": "user", "role": "writer", "emailAddress": settings.user_email},
        sendNotificationEmail=False,
    ).execute()
    log.info(f"[Docs] Shared {file_id} with {settings.user_email}")


def create_doc(settings, keyword: str) -> tuple[str, str]:
    docs = _get_docs_service(settings)
    title = f"[{keyword}] Phan tich doi thu + Ke hoach content 20 video - {date.today()}"
    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    log.info(f"[Docs] Created doc: {title} -> {url}")
    _share_if_needed(settings, doc_id)
    return doc_id, url


def _build_insert_requests(text: str) -> list[dict]:
    requests = []
    index = 1

    for line in text.splitlines(keepends=True):
        insert_req = {
            "insertText": {
                "location": {"index": index},
                "text": line,
            }
        }
        requests.append(insert_req)
        index += len(line)

    return requests


def _build_style_requests(text: str) -> list[dict]:
    requests = []
    index = 1

    for line in text.splitlines(keepends=True):
        line_text = line.rstrip("\n")
        line_len = len(line)

        if line_text.startswith("## "):
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": index + line_len},
                    "paragraphStyle": {"namedStyleType": "HEADING_2"},
                    "fields": "namedStyleType",
                }
            })
        elif line_text.startswith("# "):
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": index + line_len},
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "fields": "namedStyleType",
                }
            })
        elif line_text.startswith("**") and line_text.endswith("**"):
            stripped = line_text.strip("*")
            inner_start = index + 2
            inner_end = inner_start + len(stripped)
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": inner_start, "endIndex": inner_end},
                    "textStyle": {"bold": True},
                    "fields": "bold",
                }
            })

        index += line_len + 1

    return requests


def write_analysis(settings, keyword: str, analysis_text: str) -> str:
    doc_id, url = create_doc(settings, keyword)
    docs = _get_docs_service(settings)

    insert_requests = _build_insert_requests(analysis_text)
    if insert_requests:
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": insert_requests},
        ).execute()
        log.info(f"[Docs] Inserted {len(insert_requests)} text blocks")

    style_requests = _build_style_requests(analysis_text)
    if style_requests:
        try:
            docs.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": style_requests},
            ).execute()
            log.info(f"[Docs] Applied {len(style_requests)} style rules")
        except Exception as e:
            log.warning(f"[Docs] Style application partial error (content is fine): {e}")

    log.info(f"[Docs] Document ready -> {url}")
    return url
