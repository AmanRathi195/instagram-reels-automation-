from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from array import array
import random, math, wave, subprocess, json
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'media'/'2026-10-15'
OUT.mkdir(parents=True,exist_ok=True)
W,H=720,1280
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BEIGE='#E8E1D4'; INK='#17181A'; ACID='#E2FC6B'; RED='#FC6658'
def ft(n,b=True): return ImageFont.truetype(FONT if b else REG,n)
def label(d,txt,x,y,n=24,col=INK,b=True,anchor=None):
    d.text((x,y),txt,font=ft(n,b),fill=col,anchor=anchor)
def paper(seed,dark=False):
    rng=random.Random(seed); bg=(20,21,24) if dark else (232,225,212)
    im=Image.new('RGB',(W,H),bg); d=ImageDraw.Draw(im,'RGBA')
    for _ in range(3200):
        x=rng.randrange(W); y=rng.randrange(H); r=rng.choice([1,1,2,3]); alpha=rng.randint(5,25)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(255,255,255,alpha) if dark else (25,20,14,alpha))
    for k in range(18):
        y=rng.randrange(H);d.line((0,y,W,y+rng.randint(-3,3)),fill=(255,255,255,7) if dark else (0,0,0,8),width=1)
    return im
def scene_one():
    im=paper(41); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,20),fill=INK)
    label(d,'JUST FEELING IT',45,70,23)
    label(d,'01 / 03',W-45,73,20,anchor='ra')
    d.line((45,126,675,126),fill=INK,width=3)
    label(d,'POV: THE EX RETURNS',45,195,32)
    d.rounded_rectangle((48,335,672,1002),radius=42,fill='#242529')
    d.rounded_rectangle((74,366,646,442),radius=27,fill='#383B40')
    label(d,'‹',103,387,38,'#F5F1E8')
    label(d,'Unknown Number',163,392,27,'#F5F1E8')
    d.ellipse((570,390,593,413),fill=ACID)
    label(d,'today · 9:41 PM',360,490,19,'#AAAEB1',False,'mm')
    d.rounded_rectangle((100,553,606,747),radius=34,fill='#414349')
    label(d,'DO YOU',136,596,50,'#F9F5EE')
    label(d,'MISS ME?',136,666,50,'#F9F5EE')
    label(d,'delivered',502,769,19,'#9D9D9F',False)
    d.rounded_rectangle((125,876,584,946),radius=27,fill=ACID)
    label(d,'typing...',350,910,28,INK,False,'mm')
    label(d,'WAIT FOR IT  ↘',45,1077,35)
    d.line((45,1151,675,1151),fill=INK,width=3)
    label(d,'@just_feeling_it___',45,1183,20)
    return im
def scene_two():
    im=paper(42);d=ImageDraw.Draw(im)
    label(d,'SCREEN TIME',43,92,63)
    d.rectangle((43,185,675,195),fill=INK)
    label(d,'WEEKLY REPORT',46,260,24)
    d.rounded_rectangle((44,342,676,920),radius=42,fill='#FAF7EE',outline=INK,width=5)
    label(d,'AVERAGE SCREEN TIME',87,403,27,INK)
    label(d,'↓ 68%',80,497,100,INK)
    label(d,'from last week',90,637,27,INK,False)
    vals=[194,161,139,110,88,51,30]
    for i,v in enumerate(vals):
        x=90+i*78
        d.rounded_rectangle((x,843-v,x+45,843),radius=8,fill=ACID if i>=4 else '#A5A7A0',outline=INK,width=2)
    d.line((87,846,637,846),fill=INK,width=3)
    label(d,'MON    TUE    WED    THU    FRI    SAT    SUN',89,863,15,INK,False)
    d.rounded_rectangle((68,984,656,1082),radius=10,fill=INK)
    label(d,'THANKS FOR ASKING.',360,1032,30,ACID,True,'mm')
    label(d,'*not an actual Screen Time report',45,1193,17,INK,False)
    return im
def scene_three():
    im=paper(43,True);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,26),fill=ACID)
    label(d,'THE REPLY',45,110,27,ACID)
    d.line((45,164,675,164),fill='#777979',width=3)
    label(d,'MY',45,265,107,'#F5F0E5')
    label(d,'SCREEN',45,402,91,'#F5F0E5')
    label(d,'TIME',45,525,107,'#F5F0E5')
    d.rectangle((33,665,687,812),fill=ACID)
    label(d,'SAYS NO.',358,737,75,INK,True,'mm')
    d.arc((20,625,701,846),start=4,end=174,fill=RED,width=9)
    label(d,'SEEN. SILENCED. UNBOTHERED.',43,933,28,'#F0ECE4')
    d.line((43,1000,674,1000),fill='#727375',width=3)
    label(d,'@just_feeling_it___',43,1074,27,ACID)
    label(d,'NO REPLIES WERE HARMED.',43,1157,18,'#929391',False)
    return im
for i,im in enumerate([scene_one(),scene_two(),scene_three()]):
    im.save(OUT/f'scene_{i}.png')
scene_three().convert('RGB').save(OUT/'cover.jpg',quality=91)
frames=[77,72,79]
for i,n in enumerate(frames):
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-loop','1','-framerate','24','-i',str(OUT/f'scene_{i}.png'),'-frames:v',str(n),'-vf',"zoompan=z='min(zoom+0.0004,1.035)':d=1:s=720x1280:fps=24,format=yuv420p",'-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p',str(OUT/f'part_{i}.mp4')],check=True)
(OUT/'concat.txt').write_text(''.join("file 'part_%s.mp4'\n"%i for i in range(3)))
rate=22050; total=int(9.5*rate); samples=array('h'); rng=random.Random(404)
for i in range(total):
    t=i/rate; beat=t*1.65; frac=beat%1; pulse=math.exp(-frac*22)
    bass=math.sin(2*math.pi*(68+26*math.exp(-frac*30))*t)*pulse*.31
    hat=(rng.random()*2-1)*math.exp(-((t*3.3)%1)*50)*.055
    pad=math.sin(2*math.pi*110*t)*.022+math.sin(2*math.pi*164.8*t)*.014
    fade=min(1,t/.4,(9.5-t)/.55)
    samples.append(int(max(-1,min(1,(bass+hat+pad)*max(0,fade)))*26000))
with wave.open(str(OUT/'audio.wav'),'wb') as wav:
    wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(samples.tobytes())
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-i',str(OUT/'audio.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','96k','-t','9.5','-movflags','+faststart',str(OUT/'reel.mp4')],check=True)
meta={'date':'2026-10-15','duration_seconds':9.5,'account':'just_feeling_it___','quote':'Them: Do you miss me? / My screen time says no.','caption':'The only notification I needed was Screen Time. 💀📉\n\n#SavageQuotes #GenZHumor #ColdReplies #RelatableReels #Unbothered','status':'READY_NOT_PUBLISHED'}
(OUT/'manifest.json').write_text(json.dumps(meta,indent=2))
print('CREATED',OUT/'reel.mp4')
