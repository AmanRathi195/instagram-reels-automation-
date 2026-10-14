#!/usr/bin/env python3
"""Instagram API publishing helper. Manual test only; never auto-publishes."""
import json, os, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

BASE = "https://graph.instagram.com/v24.0"
TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
IG_ID = os.environ.get("INSTAGRAM_USER_ID", "")
def call(method, endpoint, params):
    if not TOKEN:
        raise RuntimeError("Missing INSTAGRAM_ACCESS_TOKEN secret")
    data = urllib.parse.urlencode(params).encode() if method == "POST" else None
    url = BASE + endpoint
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, data=data, method=method, headers={"Authorization": "Bearer " + TOKEN})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # Do not echo response body, which may contain sensitive information.
        raise RuntimeError(f"Instagram API returned HTTP {error.code}") from None

def verify():
    info = call("GET", "/me", {"fields": "id,username"})
    print("Instagram API authentication succeeded for @" + str(info.get("username", "unknown")))
    print("Account ID: " + str(info.get("id", "unknown")))
    return info

def publish():
    if os.environ.get("CONFIRM_INSTAGRAM_PUBLISH") != "YES":
        raise RuntimeError("Publishing is disabled. Set CONFIRM_INSTAGRAM_PUBLISH=YES for a reviewed manual test.")
    if not IG_ID:
        raise RuntimeError("Missing INSTAGRAM_USER_ID")
    video_url = os.environ.get("INSTAGRAM_VIDEO_URL", "")
    caption = os.environ.get("INSTAGRAM_CAPTION", "")
    if not video_url.startswith("https://") or not caption:
        raise RuntimeError("An immutable HTTPS video URL and caption are required")
    result = call("POST", f"/{IG_ID}/media", {"media_type": "REELS", "video_url": video_url, "caption": caption})
    creation_id = result["id"]
    for _ in range(24):
        time.sleep(15)
        status = call("GET", f"/{creation_id}", {"fields": "status_code"})
        if status.get("status_code") == "FINISHED":
            break
        if status.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError("Instagram rejected media processing")
    else:
        raise RuntimeError("Processing timed out; do not retry blindly")
    posted = call("POST", f"/{IG_ID}/media_publish", {"creation_id": creation_id})
    print("Instagram publish succeeded. Media ID: " + str(posted.get("id", "unknown")))

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2 or sys.argv[1] not in ("verify", "publish"):
            raise RuntimeError("Usage: python instagram_api.py verify|publish")
        verify() if sys.argv[1] == "verify" else publish()
    except Exception as exc:
        print("Error: " + str(exc), file=sys.stderr)
        sys.exit(1)
