#!/usr/bin/env python3
"""Automatically collect freely licensed cinematic photographs from Wikimedia Commons.
No API key, payment, or user uploads. Fail closed on unknown licenses.
"""
import json, random, re, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps
from io import BytesIO

ROOT=Path(__file__).parent
OUT=ROOT/"assets"/"daily"
OUT.mkdir(parents=True,exist_ok=True)
API="https://commons.wikimedia.org/w/api.php"
QUERIES=[
    "sunset clouds dramatic landscape",
    "fog forest silhouette",
    "moon night mountains",
    "ocean dusk cinematic",
    "rain city night",
    "golden hour meadow",
    "stars milky way landscape",
]
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"JustFeelingItReels/1.0 (open-source educational art curation; contact via GitHub)"})
    with urllib.request.urlopen(req,timeout=25) as r:return r.read()
def clean(s):return re.sub(r"<[^>]+>","",s or "").strip()
def eligible(meta):
    license_name=clean(meta.get("LicenseShortName",{}).get("value","")).lower()
    return any(x in license_name for x in ("cc by","cc0","public domain","pdm")) and "nc" not in license_name and "nd" not in license_name
def main():
    import datetime
    day=datetime.datetime.now(datetime.timezone.utc).date().toordinal()
    rng=random.Random(day)
    terms=rng.sample(QUERIES,3)
    records=[]
    for i,term in enumerate(terms):
        args={"action":"query","generator":"search","gsrsearch":term+" filetype:bitmap","gsrnamespace":"6","gsrlimit":"20","prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":"1400","format":"json"}
        try:
            data=json.loads(fetch(API+"?"+urllib.parse.urlencode(args)))
            pages=list(data.get("query",{}).get("pages",{}).values())
            rng.shuffle(pages)
            for page in pages:
                info=(page.get("imageinfo") or [{}])[0]
                meta=info.get("extmetadata",{})
                if not eligible(meta) or info.get("width",0)<900 or info.get("height",0)<600:continue
                url=info.get("thumburl") or info.get("url","")
                if not url.startswith("https://"):continue
                raw=fetch(url)
                if len(raw)>12_000_000:continue
                im=Image.open(BytesIO(raw)).convert("RGB")
                if min(im.size)<500:continue
                im=ImageOps.fit(im,(900,1600),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
                im.save(OUT/f"photo_{i}.jpg",quality=87)
                records.append({"scene":i,"title":page.get("title"),"source":info.get("descriptionurl"),"license":clean(meta.get("LicenseShortName",{}).get("value","")),"artist":clean(meta.get("Artist",{}).get("value",""))[:180]})
                break
        except Exception as exc:
            print(f"Scene {i}: could not obtain verified free photograph ({type(exc).__name__}); using local fallback")
    (OUT/"credits.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Fetched {len(records)} freely licensed photographs. Attribution saved in credits.json.")
if __name__=="__main__":main()
