#!/usr/bin/env python3
"""
Foundation for the social media posting automation.

Each run: looks in to-postMH/, picks the oldest video file, "posts" it
(currently just a placeholder print), then moves it into postedMH/.

Run this repeatedly (e.g. via cron or a loop) to work through the queue
one video at a time.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TO_POST_DIR = BASE_DIR / "to-postMH"
POSTED_DIR = BASE_DIR / "postedMH"

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}


def find_oldest_video(folder: Path) -> Path | None:
    videos = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ]
    if not videos:
        return None
    return min(videos, key=lambda f: f.stat().st_mtime)


def post_video(video: Path) -> None:
    # Placeholder for the real posting logic (YouTube, Instagram, TikTok, etc).
    print(f"Would post {video.name} now")


def main() -> int:
    TO_POST_DIR.mkdir(exist_ok=True)
    POSTED_DIR.mkdir(exist_ok=True)

    video = find_oldest_video(TO_POST_DIR)
    if video is None:
        print(f"No video files found in {TO_POST_DIR.name}/")
        return 0

    post_video(video)

    destination = POSTED_DIR / video.name
    shutil.move(str(video), str(destination))
    print(f"Moved {video.name} to {POSTED_DIR.name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
