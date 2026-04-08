"""
upload_youtube.py
-----------------
Uploads the rendered MP4 to YouTube using YouTube Data API v3.
Uses OAuth2 refresh token (generated once via get_youtube_token.py).

Reads credentials from environment variables (GitHub Secrets).
"""

import os
import json
from pathlib import Path
import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.http

OUTPUT_DIR = Path("output")

# ── Load credentials from environment ─────────────────────────────────────────
CLIENT_ID     = os.environ["YOUTUBE_CLIENT_ID"]
CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_client():
    creds = google.oauth2.credentials.Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
    )
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def upload_video():
    # Load script data for metadata
    with open(OUTPUT_DIR / "script_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    title       = data["youtube_title"]
    description = data["description"] + "\n\n" + " ".join(data["hashtags"])
    tags        = [h.replace("#", "") for h in data["hashtags"]]

    video_path = str(OUTPUT_DIR / "final_video.mp4")

    print(f"[upload_youtube] Uploading: {title}")
    print(f"[upload_youtube] File: {video_path}")

    youtube = get_youtube_client()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "25",   # 25 = News & Politics
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",   # change to "private" for testing
            "selfDeclaredMadeForKids": False,
            "madeForKids": False,
        }
    }

    media = googleapiclient.http.MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 5  # 5MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"[upload_youtube] Uploading... {pct}%")

    video_id = response.get("id")
    print(f"[upload_youtube] ✅ Video uploaded!")
    print(f"[upload_youtube] 🔗 https://www.youtube.com/watch?v={video_id}")

    # Save video ID for reference
    with open(OUTPUT_DIR / "last_upload.json", "w") as f:
        json.dump({"video_id": video_id, "title": title}, f, indent=2)


if __name__ == "__main__":
    upload_video()
