#!/usr/bin/env python3
"""
Social media posting automation.

Each run: looks in to-postMH/, picks the oldest video file, uploads it to
YouTube (title from the filename, a short generated description, generic
tags, English, "not made for kids"), then moves it into postedMH/ once the
upload succeeds.

Run this repeatedly (e.g. via cron or a loop) to work through the queue
one video at a time.

Requires token.json (see auth_youtube.py) in this directory.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = Path(__file__).resolve().parent
TO_POST_DIR = BASE_DIR / "to-postMH"
POSTED_DIR = BASE_DIR / "postedMH"
TOKEN_FILE = BASE_DIR / "token.json"

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# YouTube category ID for "People & Blogs" - a safe generic default.
CATEGORY_ID = "22"


def find_oldest_video(folder: Path) -> Path | None:
    videos = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ]
    if not videos:
        return None
    return min(videos, key=lambda f: f.stat().st_mtime)


def title_from_filename(video: Path) -> str:
    name = video.stem
    name = re.sub(r"[_-]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or video.stem


def build_description(title: str) -> str:
    return f"{title}\n\nWatch to the end!"


def build_tags(title: str) -> list[str]:
    words = re.findall(r"[^\W\d_]+", title.lower())
    tags = [w for w in words if len(w) > 2]
    tags.append("shorts")
    # De-duplicate while preserving order.
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    return unique_tags


def get_credentials() -> Credentials:
    if not TOKEN_FILE.exists():
        raise SystemExit(
            f"Missing {TOKEN_FILE.name} - run auth_youtube.py first to authorize."
        )

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())
        TOKEN_FILE.chmod(0o600)

    return creds


def upload_video(youtube, video: Path) -> str:
    title = title_from_filename(video)
    body = {
        "snippet": {
            "title": title,
            "description": build_description(title),
            "tags": build_tags(title),
            "categoryId": CATEGORY_ID,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "selfDeclaredMadeForKids": False,
            "privacyStatus": "private",
        },
    }

    media = MediaFileUpload(str(video), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading {video.name}: {int(status.progress() * 100)}%")

    return response["id"]


def main() -> int:
    TO_POST_DIR.mkdir(exist_ok=True)
    POSTED_DIR.mkdir(exist_ok=True)

    video = find_oldest_video(TO_POST_DIR)
    if video is None:
        print(f"No video files found in {TO_POST_DIR.name}/")
        return 0

    credentials = get_credentials()
    youtube = build("youtube", "v3", credentials=credentials)

    video_id = upload_video(youtube, video)
    print(f"Uploaded {video.name} as https://youtu.be/{video_id}")

    destination = POSTED_DIR / video.name
    shutil.move(str(video), str(destination))
    print(f"Moved {video.name} to {POSTED_DIR.name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
