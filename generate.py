#!/usr/bin/env python3
"""Credit-free, story-first Instagram Reel generator. Preview only, never publishes."""
import datetime, json, math, random, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).parent
OUT=ROOT/"site"
OUT.mkdir(exist_ok=True)
stories=json.loads((ROOT/"content/stories.json").read_text(encoding="utf-8"))
today=datetime.datetime.now(datetime.timezone.utc).date()
story=stories[(today.toordinal()-datetime.date(2026,10,14).toordinal())%len(stories)]
W,H=720,1280
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regularfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(n,bold=True):
    return ImageFont.truetype(fontfile if bold else regularfile,n)
def center(d,txt,y,size=47,color="#FFFFFF",maxwidth=625):
    f=font(size)
    words=txt.split(); lines=[]; line=""
    for word in words:
        test=(line+" "+word).strip()
        if d.textbbox((0,0),test,font=f)[2]>maxwidth and line:
            lines.append(line);line=word
        else:line=test
    if line:lines.append(line)
    for k,t in enumerate(lines):
        d.text((W//2,y+k*(size+16)),t,font=f,anchor="mt",fill=color,stroke_width=1,stroke_fill="#14101D")
    return y+len(lines)*(size+16)
def background(theme,scene):
    rng=random.Random(today.toordinal()*7+scene*19)
    im=Image.new("RGB",(W,H)); d=ImageDraw.Draw(im)
    a,b=theme
    for y in range(H):
        p=y/(H-1)
        col=tuple(int(a[k]*(1-p)+b[k]*p) for k in range(3))
        d.line((0,y,W,y),fill=col)
    for i in range(14):
        x=rng.randint(-160,W+160);y=rng.randint(-120,H+120);r=rng.randint(20,180)
        d.ellipse((x-r,y-r,x+r,y+r),outline=(70,64,87),width=rng.randint(1,3))
    return im
def pill(d,text,y,fill="#F1C15C"):
    f=font(22)
    bb=d.textbbox((0,0),text,font=f)
    ww=bb[2]+50
    d.rounded_rectangle((W//2-ww//2,y,W//2+ww//2,y+54),radius=27,fill=fill)
    d.text((W//2,y+27),text,font=f,fill="#16121B",anchor="mm")
def chat_bubble(d,text,y,right=False,accent=False):
    x0=132 if right else 44; x1=676 if right else 588
    col="#5D4679" if right else "#272638"
    d.rounded_rectangle((x0,y,x1,y+210),radius=32,fill=col)
    f=font(31)
    words=text.split();lines=[];line=""
    for word in words:
        test=(line+" "+word).strip()
        if d.textbbox((0,0),test,font=f)[2]>445 and line:
            lines.append(line);line=word
        else:line=test
    if line:lines.append(line)
    for i,t in enumerate(lines[:4]):
        d.text((x0+26,y+36+i*45),t,font=f,fill="#F8F4FF")
    d.text((x1-20,y+178),"✓✓" if right else "now",font=font(18,False),fill="#E8B45F" if accent else "#AAA5B9",anchor="ra")
def draw_scene(idx):
    themes=[((11,13,24),(28,19,45)),((12,19,30),(24,33,53)),((30,12,26),(57,21,47))]
    im=background(themes[idx],idx);d=ImageDraw.Draw(im)
    d.rounded_rectangle((34,47,686,1218),radius=45,outline="#6C5D78",width=3)
    d.text((W//2,91),"JUST FEELING IT",font=font(21),anchor="mm",fill="#C5B6D1")
    d.line((85,140,635,140),fill="#56485E",width=2)
    if idx==0:
        pill(d,"THE AUDACITY",202)
        center(d,story["hook"],318,56)
        d.rounded_rectangle((62,620,658,928),radius=38,fill="#25243A")
        d.text((W//2,674),"POV",font=font(30),anchor="mm",fill="#EFC16D")
        center(d,story["setup"],735,40,maxwidth=510)
        center(d,"WAIT FOR THE REPLY  →",1050,24,color="#C6B5D8")
    elif idx==1:
        pill(d,"THE CONVERSATION",205,fill="#C8A9FF")
        d.text((70,312),"MESSAGES",font=font(24),fill="#C8B7D9")
        chat_bubble(d,story["setup"],410,False)
        chat_bubble(d,"typing…",725,True)
        d.text((W//2,1040),"seen  •  8:42 PM",font=font(23,False),anchor="mm",fill="#A9A2B8")
    else:
        pill(d,"THE REPLY",212)
        d.rounded_rectangle((54,366,666,824),radius=40,fill="#2A2138",outline="#C7A3D3",width=3)
        center(d,story["reply"],458,52,color="#FFF6E9",maxwidth=515)
        center(d,story["tagline"],922,34,color="#EAC27C")
        d.text((W//2,1116),"@just_feeling_it___",font=font(24),anchor="mm",fill="#C8BED0")
    filename=OUT/f"scene_{idx}.png";im.save(filename)
    return filename
for i in range(3):draw_scene(i)
# Each scene has subtle camera motion; three distinct beats, with original synthesized audio.
segments=[]
for i in range(3):
    target=OUT/f"part_{i}.mp4"
    vf="zoompan=z='min(zoom+0.00065,1.07)':d=1:s=720x1280:fps=24,format=yuv420p"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate","24","-i",str(OUT/f"scene_{i}.png"),"-t","3","-vf",vf,"-an","-c:v","libx264","-preset","veryfast","-crf","25","-pix_fmt","yuv420p",str(target)],check=True)
    segments.append(target)
listfile=OUT/"concat.txt"
listfile.write_text("".join("file '"+p.name+"'\n" for p in segments),encoding="utf-8")
# Original minimal electronic sound bed, no copyrighted music.
audio="[0:a]volume=0.045,afade=t=in:st=0:d=0.3,afade=t=out:st=8.3:d=0.7[a]"
video=OUT/"reel.mp4"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listfile),"-f","lavfi","-i","sine=frequency=110:sample_rate=44100:duration=9","-filter_complex",audio,"-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","96k","-movflags","+faststart",str(video)],check=True)
caption=story["caption"]+"\n\n"+story["tags"]
(OUT/"manifest.json").write_text(json.dumps({"date":today.isoformat(),"caption":caption,"video":"reel.mp4","status":"PREVIEW_ONLY","format":"three-act-chat-reveal"},indent=2),encoding="utf-8")
(OUT/"index.html").write_text('<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body style="background:#14121c;color:white;font-family:sans-serif;text-align:center"><h2>Reel preview — not published</h2><video src="reel.mp4" controls playsinline style="max-width:95%;max-height:85vh"></video></body></html>',encoding="utf-8")
print("Generated preview-only Reel for",today)
