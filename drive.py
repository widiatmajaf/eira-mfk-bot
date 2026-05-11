import json
import base64
import asyncio
from io import BytesIO
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from config import GOOGLE_CREDENTIALS, FOLDER_TOILET, FOLDER_GENSET, FOLDER_MFK

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

FOLDER_MAP = {
    "FOLDER_TOILET": FOLDER_TOILET,
    "FOLDER_GENSET": FOLDER_GENSET,
    "FOLDER_MFK": FOLDER_MFK,
}


def _get_service():
    creds_dict = json.loads(base64.b64decode(GOOGLE_CREDENTIALS))
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _upload_sync(file_bytes: bytes, filename: str, folder_id: str) -> str:
    service = _get_service()
    file_meta = {"name": filename, "parents": [folder_id]}
    media = MediaIoBaseUpload(BytesIO(file_bytes), mimetype="image/jpeg")
    result = service.files().create(
        body=file_meta, media_body=media, fields="id,webViewLink"
    ).execute()
    # Make shareable
    service.permissions().create(
        fileId=result["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()
    return result["webViewLink"]


async def upload_photo(file_bytes: bytes, filename: str, folder_key: str) -> str | None:
    """Upload photo to Google Drive. Returns shareable link or None."""
    folder_id = FOLDER_MAP.get(folder_key, "")
    if not folder_id or not GOOGLE_CREDENTIALS:
        return None
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, _upload_sync, file_bytes, filename, folder_id)
    except Exception as e:
        print(f"Drive upload error: {e}")
        return None
