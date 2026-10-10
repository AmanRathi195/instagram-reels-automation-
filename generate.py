#!/usr/bin/env python3
"""Credit-free 9-second vertical typography Reel generator."""
import datetime, json, math, os, random, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUT = ROOT / "site"
OUT.mkdir(exist_ok=True)
items = json.loads((ROOT / "content/quotes.json").read_text(encoding="utf-8"))
today = datetime.datetime.now(datetime.timezone.utc).date()
index = (today.toordinal() - datetime.date(2026, 10, 10).toordinal()) % len(items)
item = items[index]
random.seed(today.toordinal())
W, H = 1080, 1920
palettes = [((12, 16, 29), (38, 22, 52)), ((9, 25, 32), (19, 54, 61)), ((27, 15, 21), (71, 30, 40)), ((16, 17, 23), (49, 48, 66))]
top, bottom = palettes[index % len(palettes)]
im = Image.new("RGB", (W, H))
pix = im.load()
for y in range(H):
    a = y / (H - 1)
    c = tuple(int(top[k] * (1-a) + bottom[k] * a) for k in range(3))
    for x in range(W):
        pix[x, y] = c
d = ImageDraw.Draw(im)
for i in range(22):
    x, y = random.randrange(W), random.randrange(H)
    r = random.randrange(1, 5)
    d.ellipse((x-r, y-r, x+r, y+r), fill=(91, 88, 104))
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(font_path, 68)
small = ImageFont.truetype(font_path, 29)
words = item["quote"].split()
lines, current = [], ""
for word in words:
    attempt = (current + " " + word).strip()
    if d.textbbox((0,0), attempt, font=font)[2] > 875 and current:
        lines.append(current)
        current = word
    else:
        current = attempt
if current: lines.append(current)
line_h = 103
y0 = H//2 - len(lines)*line_h//2
for j, line in enumerate(lines):
    width = d.textbbox((0,0), line, font=font)[2]
    d.text(((W-width)//2, y0+j*line_h), line, font=font, fill=(245, 242, 240))
d.rounded_rectangle((425, y0-90, 655, y0-82), radius=4, fill=(223, 114, 130))
d.text((W//2, 1650), "@just_feeling_it___", font=small, fill=(185, 181, 190), anchor="mm")
background = OUT / "background.png"
im.save(background)
video = OUT / "reel.mp4"
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", "30", "-i", str(background), "-t", "9", "-vf", "fade=t=in:st=0:d=0.5,fade=t=out:st=8.5:d=0.5,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video)], check=True)
(OUT / "manifest.json").write_text(json.dumps({"date":today.isoformat(), "quote":item["quote"], "caption":item["caption"], "hashtags":item["tags"], "video":"reel.mp4"}, indent=2), encoding="utf-8")
(OUT / "index.html").write_text('<!doctype html><html><head><meta name="robots" content="noindex"></head><body><h1>Instagram Reel media</h1><p>Public media endpoint; no credentials stored here.</p><a href="reel.mp4">Current Reel</a></body></html>', encoding="utf-8")
print(f"Generated {video} for {today}: {item['quote']}")
