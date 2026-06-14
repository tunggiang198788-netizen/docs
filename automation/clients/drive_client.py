from __future__ import annotations

from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import log

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_service(service_account_json: str):
    creds = Credentials.from_service_account_file(service_account_json, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def create_folder(service_account_json: str, name: str, parent_id: str = "") -> str:
    service = _get_service(service_account_json)
    metadata: dict = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(body=metadata, fields="id").execute()
    folder_id = folder["id"]
    log.info(f"[Drive] Created folder '{name}' → id={folder_id}")
    return folder_id


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=16))
def upload_file(service_account_json: str, local_path: Path, folder_id: str) -> str:
    service = _get_service(service_account_json)
    metadata: dict = {"name": local_path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(local_path), mimetype="video/mp4", resumable=True)
    file = (
        service.files()
        .create(body=metadata, media_body=media, fields="id,webViewLink")
        .execute()
    )
    url = file.get("webViewLink", f"https://drive.google.com/file/d/{file['id']}/view")
    log.info(f"[Drive] Uploaded {local_path.name} → {url}")
    return url


def upload_all_videos(
    service_account_json: str,
    local_paths: list[Path],
    keyword: str,
    parent_folder_id: str = "",
) -> tuple[str, list[str]]:
    folder_name = f"{keyword} - Top {len(local_paths)} Videos"
    folder_id = create_folder(service_account_json, folder_name, parent_folder_id)
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

    file_urls: list[str] = []
    for path in local_paths:
        try:
            url = upload_file(service_account_json, path, folder_id)
            file_urls.append(url)
        except Exception as e:
            log.warning(f"[Drive] Failed to upload {path.name}: {e}")
            file_urls.append("")

    log.info(f"[Drive] Uploaded {len([u for u in file_urls if u])}/{len(local_paths)} files")
    return folder_url, file_urls
