#!/usr/bin/env python3
"""Fail the preview workflow if the Reel is technically invalid."""
import json, subprocess
from pathlib import Path
p=Path("site/reel.mp4")
if not p.exists() or p.stat().st_size<100_000:
    raise SystemExit("Reel missing or suspiciously small")
result=subprocess.run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(p)],capture_output=True,text=True,check=True)
info=json.loads(result.stdout)
streams=info["streams"]
video=next((s for s in streams if s.get("codec_type")=="video"),None)
audio=next((s for s in streams if s.get("codec_type")=="audio"),None)
duration=float(info["format"]["duration"])
if not video or video.get("codec_name")!="h264" or int(video["width"])!=720 or int(video["height"])!=1280:
    raise SystemExit("Invalid vertical H.264 video")
if not audio or audio.get("codec_name")!="aac":
    raise SystemExit("Missing AAC audio")
if not 14.5<=duration<=15.5:
    raise SystemExit(f"Unexpected duration: {duration}")
print(f"PASS: {duration:.2f}s vertical H264/AAC Reel, {p.stat().st_size/1e6:.1f} MB")
