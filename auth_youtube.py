#!/usr/bin/env python3
"""
One-time local authorization script for YouTube uploads.

Run this once: it opens your browser, has you log into the YouTube
account you want to post to, and saves the resulting credentials
(including a refresh token) to token.json. Later scripts (e.g. the
posting script) can load token.json to make authenticated API calls
without repeating the browser login.

Requires: pip install google-auth-oauthlib google-api-python-client
"""

from __future__ import annotations

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

# Upload-only scope, sufficient for posting videos.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> int:
    if not CREDENTIALS_FILE.exists():
        print(f"Missing {CREDENTIALS_FILE.name} in {BASE_DIR} - "
              "download your OAuth client credentials from Google Cloud "
              "Console and place them there first.")
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    credentials = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(credentials.to_json())
    TOKEN_FILE.chmod(0o600)
    print(f"Saved credentials to {TOKEN_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
