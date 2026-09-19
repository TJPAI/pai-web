#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/images/social/pai-share-v2.png'
W,H=1200,630
img=Image.new('RGB',(W,H),(248,249,251))
d=ImageDraw.Draw(img)

# Subtle cool-gray geometry kept outside the central safe crop.
for x,y,r in [(95,90,4),(1080,105,5),(1125,515,3),(80,520,3)]:
    d.ellipse((x-r,y-r,x+r,y+r),fill=(164,178,195))
for y in (86,544):
    d.line((70,y,1130,y),fill=(224,228,234),width=2)

font_dirs=[Path('/usr/share/fonts/truetype/dejavu'),Path('/usr/share/fonts/truetype/liberation2')]
def font(name,size):
    candidates=[]
    if name=='bold':
        candidates=['DejaVuSans-Bold.ttf','LiberationSans-Bold.ttf']
    else:
        candidates=['DejaVuSans.ttf','LiberationSans-Regular.ttf']
    for base in font_dirs:
        for c in candidates:
            p=base/c
            if p.exists(): return ImageFont.truetype(str(p),size=size)
    return ImageFont.load_default()

f_pai=font('bold',188)
f_rc=font('bold',64)
f_tj=font('regular',31)
f_micro=font('regular',20)
ink=(23,26,31)
muted=(100,112,133)
blue=(49,138,245)

def center(text,f,y,fill,spacing=0):
    box=d.textbbox((0,0),text,font=f)
    x=(W-(box[2]-box[0]))/2
    d.text((x,y),text,font=f,fill=fill)

# Central safe zone: survives square thumbnails/crops.
center('PAI',f_pai,130,ink)
center('Research Center',f_rc,335,ink)
center('Tongji University',f_tj,430,muted)

# Compact accent, still visible when downscaled.
d.rounded_rectangle((500,495,700,502),radius=4,fill=blue)
center('SENSING · COMMUNICATION · COMPUTING · INTELLIGENCE',f_micro,523,muted)

OUT.parent.mkdir(parents=True,exist_ok=True)
img.save(OUT,optimize=True)

old='https://tjpai.github.io/pai-web/assets/images/social/pai-share.png'
new='https://tjpai.github.io/pai-web/assets/images/social/pai-share-v2.png'
for p in ROOT.rglob('*.html'):
    text=p.read_text(encoding='utf-8')
    if old in text:
        p.write_text(text.replace(old,new),encoding='utf-8')

# Guard against future accidental fallback to the old social card.
vp=ROOT/'tools/validate.py'
v=vp.read_text(encoding='utf-8')
marker='# Social preview guardrail.'
if marker not in v:
    guard='''\n\n# Social preview guardrail.\nfor html,text in html_text.items():\n    rel=str(Path(html).relative_to(ROOT))\n    if 'pai-share.png' in text:\n        errors.append(f'{rel}: legacy social preview image reference remains; use pai-share-v2.png')\n    if 'property="og:image"' in text and 'pai-share-v2.png' not in text:\n        errors.append(f'{rel}: og:image must use the compact social preview image')\n'''
    insert=v.rfind("if errors:")
    if insert==-1: raise SystemExit('validate.py final error block not found')
    v=v[:insert]+guard+'\n'+v[insert:]
    vp.write_text(v,encoding='utf-8')

print('updated social preview v2')
