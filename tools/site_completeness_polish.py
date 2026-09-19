#!/usr/bin/env python3
from pathlib import Path
import json,re
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
BASE='https://tjpai.github.io/pai-web'
VERSION='20260919-11'

# ---------- Brand assets ----------
def font(size,bold=False):
    paths=[
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
    ]
    for p in paths:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

icons=ROOT/'assets/icons'; icons.mkdir(parents=True,exist_ok=True)
social=ROOT/'assets/images/social'; social.mkdir(parents=True,exist_ok=True)

# SVG favicon remains crisp at arbitrary browser sizes.
(icons/'favicon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#171A1F"/><path d="M14 43V19h12.2c6.6 0 10.7 3.5 10.7 9.2 0 5.8-4.1 9.4-10.7 9.4h-6.1V43H14zm6.1-10.4h5.5c3.3 0 5.1-1.5 5.1-4.3 0-2.7-1.8-4.2-5.1-4.2h-5.5v8.5zM40 43V19h6.2v24H40z" fill="#fff"/><circle cx="52" cy="19" r="4" fill="#318AF5"/></svg>''',encoding='utf-8')

def make_icon(size,path):
    im=Image.new('RGB',(size,size),'#171A1F'); d=ImageDraw.Draw(im)
    f=font(max(12,int(size*.27)),True)
    text='PAI'
    box=d.textbbox((0,0),text,font=f)
    x=(size-(box[2]-box[0]))/2; y=(size-(box[3]-box[1]))/2-box[1]
    d.text((x,y),text,font=f,fill='white')
    r=max(2,size//32); d.ellipse((size*.78-r,size*.20-r,size*.78+r,size*.20+r),fill='#318AF5')
    im.save(path,optimize=True)

for size,name in [(32,'favicon-32.png'),(180,'apple-touch-icon.png'),(192,'icon-192.png'),(512,'icon-512.png')]:
    make_icon(size,icons/name)

# 1200x630 social share card: restrained, typography-led, consistent with the site.
w,h=1200,630
im=Image.new('RGB',(w,h),'#F6F7F9'); d=ImageDraw.Draw(im)
# quiet network motif on the right
pts=[(790,430),(875,355),(940,375),(1010,285),(1100,215),(1145,150)]
for a,b in zip(pts,pts[1:]): d.line((a,b),fill='#D5DAE1',width=2)
for x,y in pts: d.ellipse((x-6,y-6,x+6,y+6),fill='#AAB3BF')
for i in range(6):
    d.line((760+i*55,120,1110-i*25,480),fill='#ECEFF3',width=1)
# typography
ink='#171A1F'; muted='#667085'; blue='#318AF5'
d.text((78,72),'PAI',font=font(42,True),fill=ink)
d.text((78,130),'RESEARCH CENTER',font=font(18,True),fill=muted)
d.rectangle((78,182,132,188),fill=blue)
d.text((78,235),'Perception. Connectivity.',font=font(52,True),fill=ink)
d.text((78,300),'Trusted Intelligence.',font=font(52,True),fill=ink)
d.text((78,405),'Tongji University',font=font(25,False),fill=muted)
d.text((78,475),'Integrated Sensing · Communication · Computing · Intelligence',font=font(19,False),fill=muted)
im.save(social/'pai-share.png',optimize=True)

manifest={
  'name':'PAI Research Center · Tongji University',
  'short_name':'PAI',
  'start_url':'./',
  'display':'standalone',
  'background_color':'#ffffff',
  'theme_color':'#171A1F',
  'icons':[
    {'src':'assets/icons/icon-192.png','sizes':'192x192','type':'image/png'},
    {'src':'assets/icons/icon-512.png','sizes':'512x512','type':'image/png'}
  ]
}
(ROOT/'site.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

# ---------- HTML helpers ----------
def rel_prefix(rel):
    depth=len(Path(rel).parts)-1
    return '../'*depth

def canonical_url(rel):
    if rel=='index.html': return BASE+'/'
    if rel=='en/index.html': return BASE+'/en/'
    return BASE+'/'+rel

def enhance_head(rel,text):
    pref=rel_prefix(rel)
    # unify cache version
    text=re.sub(r'v=20260919-(?:8|9|10)',f'v={VERSION}',text)
    # remove prior generated asset metadata if rerun
    patterns=[
      r'<link rel="icon"[^>]*>',r'<link rel="apple-touch-icon"[^>]*>',r'<link rel="manifest"[^>]*>',
      r'<meta name="theme-color"[^>]*>',r'<meta property="og:image"[^>]*>',r'<meta property="og:image:width"[^>]*>',
      r'<meta property="og:image:height"[^>]*>',r'<meta property="og:image:alt"[^>]*>',r'<meta property="og:locale"[^>]*>',
      r'<meta name="twitter:card"[^>]*>',r'<meta name="twitter:title"[^>]*>',r'<meta name="twitter:description"[^>]*>',r'<meta name="twitter:image"[^>]*>'
    ]
    for pat in patterns: text=re.sub(pat,'',text)
    title=re.search(r'<title>(.*?)</title>',text,re.S).group(1)
    desc=re.search(r'<meta name="description" content="([^"]*)">',text).group(1)
    lang='en' if rel.startswith('en/') else 'zh-CN'
    meta=(
      f'<link rel="icon" type="image/svg+xml" href="{pref}assets/icons/favicon.svg">'
      f'<link rel="icon" type="image/png" sizes="32x32" href="{pref}assets/icons/favicon-32.png">'
      f'<link rel="apple-touch-icon" sizes="180x180" href="{pref}assets/icons/apple-touch-icon.png">'
      f'<link rel="manifest" href="{pref}site.webmanifest">'
      f'<meta name="theme-color" content="#171A1F">'
      f'<meta property="og:image" content="{BASE}/assets/images/social/pai-share.png">'
      f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
      f'<meta property="og:image:alt" content="PAI Research Center · Tongji University">'
      f'<meta property="og:locale" content="{"en_US" if lang=="en" else "zh_CN"}">'
      f'<meta name="twitter:card" content="summary_large_image">'
      f'<meta name="twitter:title" content="{title}">'
      f'<meta name="twitter:description" content="{desc}">'
      f'<meta name="twitter:image" content="{BASE}/assets/images/social/pai-share.png">'
    )
    return text.replace('</head>',meta+'</head>')

def add_accessibility(rel,text):
    en=rel.startswith('en/')
    label='Skip to main content' if en else '跳到主要内容'
    if 'class="skip-link"' not in text:
        text=text.replace('<body>','<body><a class="skip-link" href="#main-content">'+label+'</a>',1)
    text=text.replace('<main>','<main id="main-content">',1)
    # static shell semantics; site.js will keep these synchronized after lightweight navigation.
    text=re.sub(r'<nav class="nav-links"(?![^>]*aria-label)',f'<nav class="nav-links" aria-label="{"Main navigation" if en else "主导航"}"',text)
    text=re.sub(r'<nav class="mobile-menu"(?![^>]*aria-label)',f'<nav class="mobile-menu" id="mobile-navigation" aria-label="{"Mobile navigation" if en else "移动导航"}"',text)
    text=re.sub(r'<button class="menu-btn"([^>]*)>',lambda m:'<button class="menu-btn"'+m.group(1)+((' aria-expanded="false"' if 'aria-expanded=' not in m.group(1) else '')+(' aria-controls="mobile-navigation"' if 'aria-controls=' not in m.group(1) else ''))+'>',text)
    return text

ORG={
 '@context':'https://schema.org','@type':'ResearchOrganization','@id':BASE+'/#organization',
 'name':'PAI Research Center','alternateName':'同济大学 PAI 研究中心','url':BASE+'/',
 'parentOrganization':{'@type':'CollegeOrUniversity','name':'Tongji University','url':'https://www.tongji.edu.cn/'},
 'address':{'@type':'PostalAddress','streetAddress':"4800 Cao'an Highway",'addressLocality':'Shanghai','addressRegion':'Shanghai','addressCountry':'CN'},
 'email':'23666042@tongji.edu.cn',
 'knowsAbout':['high-precision localization','intelligent sensing','robust communications','reliable networking','artificial intelligence','blockchain','trusted collaboration','integrated sensing, communication, computing, and intelligence']
}
PEOPLE={
 'erwu-liu':('刘儿兀','Erwu Liu','Professor · Director',['wireless communications','IoT','localization and sensing','artificial intelligence','blockchain']),
 'rui-wang':('王睿','Rui Wang','Professor',['wireless communications','machine learning','signal processing','ISAC']),
 'gang-shen':('沈钢','Gang Shen','Professor-level Senior Engineer',['6G','foundation models for communications','agent communications','ISAC']),
 'dunhui-xiao':('肖敦辉','Dunhui Xiao','Professor',['computational mathematics','data science','AI for Engineering']),
 'shuyan-hu':('胡淑彦','Shuyan Hu','Associate Professor',['machine learning','integrated sensing, communication and computing','space-air-ground networks']),
 'yan-liu':('刘燕','Yan Liu','Assistant Professor',['IoT communications','random access','machine learning'])
}

def add_schema(rel,text):
    # Remove generated schema if rerun.
    text=re.sub(r'<script type="application/ld\+json" data-pai-schema>.*?</script>','',text,flags=re.S)
    obj=None
    if rel in ('index.html','en/index.html'):
        obj=ORG
    else:
        m=re.fullmatch(r'(?:en/)?people/([^/]+)\.html',rel)
        if m and m.group(1) in PEOPLE:
            slug=m.group(1); zh,enname,job,topics=PEOPLE[slug]
            is_en=rel.startswith('en/')
            obj={
              '@context':'https://schema.org','@type':'Person','@id':canonical_url(rel)+'#person',
              'name':enname if is_en else zh,'alternateName':zh if is_en else enname,'jobTitle':job,
              'url':canonical_url(rel),'image':BASE+'/assets/images/people/'+slug+('.png' if slug=='gang-shen' else '.jpg'),
              'affiliation':{'@type':'CollegeOrUniversity','name':'Tongji University','url':'https://www.tongji.edu.cn/'},
              'memberOf':{'@id':BASE+'/#organization'},'knowsAbout':topics
            }
    if obj:
        script='<script type="application/ld+json" data-pai-schema>'+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'</script>'
        text=text.replace('</head>',script+'</head>')
    return text

# ---------- Selected homepage updates ----------
ZH_UPDATES='''<section class="section selected-updates" id="selected-updates"><div class="container"><div class="section-head"><div class="eyebrow">SELECTED UPDATES</div><h2 class="title-section">精选动态</h2></div><div class="updates-grid"><article class="update-item"><div class="update-meta">国际平台</div><h3 class="title-item">IEEE Global Blockchain Conference</h3><p>建设国际区块链学术交流与产业合作平台。</p><a class="text-link" href="about.html#international-impact">了解平台影响 →</a></article><article class="update-item"><div class="update-meta">应用实践</div><h3 class="title-item">中国国际进口博览会智能导览系统</h3><p>高精定位与智能导航技术应用于国家会展中心大型复杂场馆。</p><a class="text-link" href="about.html#achievements">查看代表成果 →</a></article><article class="update-item"><div class="update-meta">国际期刊</div><h3 class="title-item">IET Blockchain</h3><p>持续参与国际期刊平台建设与区块链领域学术交流。</p><a class="text-link" href="about.html#international-impact">了解国际平台 →</a></article></div></div></section>'''
EN_UPDATES='''<section class="section selected-updates" id="selected-updates"><div class="container"><div class="section-head"><div class="eyebrow">SELECTED UPDATES</div><h2 class="title-section">Selected Updates</h2></div><div class="updates-grid"><article class="update-item"><div class="update-meta">INTERNATIONAL PLATFORM</div><h3 class="title-item">IEEE Global Blockchain Conference</h3><p>An international platform for blockchain research, technical exchange and industry collaboration.</p><a class="text-link" href="about.html#international-impact">Explore international engagement →</a></article><article class="update-item"><div class="update-meta">APPLICATION</div><h3 class="title-item">Smart Navigation for the China International Import Expo</h3><p>High-precision localization and intelligent navigation deployed at the National Exhibition and Convention Center.</p><a class="text-link" href="about.html#achievements">Explore selected achievements →</a></article><article class="update-item"><div class="update-meta">JOURNAL</div><h3 class="title-item">IET Blockchain</h3><p>Ongoing editorial and community engagement in blockchain and trusted digital systems.</p><a class="text-link" href="about.html#international-impact">Explore international engagement →</a></article></div></div></section>'''

def add_updates(rel,text):
    if rel not in ('index.html','en/index.html'): return text
    text=re.sub(r'<section class="section selected-updates".*?</section>','',text,flags=re.S)
    block=EN_UPDATES if rel.startswith('en/') else ZH_UPDATES
    return text.replace('<section class="join">',block+'<section class="join">',1)

# Process all main bilingual pages and faculty details.
rels=['index.html','about.html','research.html','team.html','publications.html','join.html','contact.html']
rels += ['en/'+x for x in rels]
for slug in PEOPLE:
    rels += [f'people/{slug}.html',f'en/people/{slug}.html']
for rel in rels:
    p=ROOT/rel
    text=p.read_text(encoding='utf-8')
    text=enhance_head(rel,text)
    text=add_accessibility(rel,text)
    text=add_updates(rel,text)
    text=add_schema(rel,text)
    p.write_text(text,encoding='utf-8')

# ---------- CSS ----------
app=ROOT/'assets/css/app-core.css'
css=app.read_text(encoding='utf-8')
css=re.sub(r'/\* Site completeness polish — 2026-09-19 \*/.*\Z','',css,flags=re.S).rstrip()+'''\n\n/* Site completeness polish — 2026-09-19 */
.skip-link{position:fixed;left:16px;top:10px;z-index:9999;transform:translateY(-150%);padding:9px 13px;border-radius:4px;background:#171A1F;color:#fff;font-size:13px;font-weight:650;text-decoration:none;transition:transform .14s ease}
.skip-link:focus{transform:none}
a:focus-visible,button:focus-visible{outline:2px solid #318AF5;outline-offset:3px}
.updates-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;border-top:1px solid var(--line)}
.update-item{padding:28px 34px 30px 0;border-bottom:1px solid var(--line)}
.update-item+.update-item{padding-left:34px;border-left:1px solid var(--line)}
.update-meta{margin-bottom:15px;font-size:11px;line-height:1.3;font-weight:700;letter-spacing:.12em;color:var(--muted)}
.update-item h3{margin:0 0 12px}
.update-item p{margin:0 0 17px;color:var(--muted);line-height:1.68}
@media(max-width:768px){
  .menu-btn:focus-visible{outline:0!important;box-shadow:0 0 0 3px rgba(49,138,245,.25)!important;border-radius:8px!important}
  .updates-grid{grid-template-columns:1fr}
  .update-item,.update-item+.update-item{padding:24px 0 26px;border-left:0}
  .update-meta{margin-bottom:12px}
  .update-item p{margin-bottom:14px}
}
'''
app.write_text(css,encoding='utf-8')

# Update refine nested import cache version.
ref=ROOT/'assets/css/refine.css'
r=ref.read_text(encoding='utf-8')
r=re.sub(r'v=20260919-(?:8|9|10)',f'v={VERSION}',r)
ref.write_text(r,encoding='utf-8')

# ---------- Runtime accessibility ----------
js_path=ROOT/'assets/js/site.js'
js=js_path.read_text(encoding='utf-8')
js=js.replace("return `<a${key===active?' class=\"active\"':''} href=\"${root(href)}\">${label}</a>`;","return `<a${key===active?' class=\"active\" aria-current=\"page\"':''} href=\"${root(href)}\">${label}</a>`;")
js=js.replace("if(nav) nav.innerHTML=markup;","if(nav){ nav.setAttribute('aria-label',lang==='en'?'Main navigation':'主导航'); nav.innerHTML=markup; }")
js=js.replace("mobile.innerHTML=markup;\n      mobile.classList.remove('open');","mobile.id='mobile-navigation';\n      mobile.setAttribute('aria-label',lang==='en'?'Mobile navigation':'移动导航');\n      mobile.innerHTML=markup;\n      mobile.classList.remove('open');")
js=js.replace("button.setAttribute('aria-expanded','false');\n        button.setAttribute('aria-label',lang==='en'?'Open menu':'打开菜单');","button.setAttribute('aria-expanded','false');\n        button.setAttribute('aria-controls','mobile-navigation');\n        button.setAttribute('aria-label',lang==='en'?'Open menu':'打开菜单');")
needle="""  document.addEventListener('click',event=>{\n    const link=event.target.closest&&event.target.closest('a');"""
escape="""  document.addEventListener('keydown',event=>{\n    if(event.key!=='Escape') return;\n    const header=document.querySelector('.site-header');\n    const menu=header?.querySelector('.mobile-menu');\n    const button=header?.querySelector('.menu-btn');\n    if(!menu?.classList.contains('open')) return;\n    menu.classList.remove('open');\n    if(button){ button.setAttribute('aria-expanded','false'); button.focus(); }\n  });\n\n"""
if escape.strip() not in js:
    js=js.replace(needle,escape+needle,1)
js_path.write_text(js,encoding='utf-8')

# ---------- Validator guardrails ----------
val=ROOT/'tools/validate.py'
v=val.read_text(encoding='utf-8')
marker='# PAI terminology / completeness guardrails.'
if marker not in v:
    insert='''\n\n# PAI terminology / completeness guardrails.\n_deprecated_pai_terms=[\n    '通信–定位–感知融合','通信-定位-感知融合','通信—定位—感知融合',\n    'integrated communication, localization and sensing'\n]\nfor html,text in html_text.items():\n    rel=str(Path(html).relative_to(ROOT))\n    lower=text.lower()\n    for term in _deprecated_pai_terms:\n        if term.lower() in lower:\n            errors.append(f'{rel}: deprecated PAI integration terminology: {term}')\nfor rel,required in [\n    ('index.html','通信–感知–计算–智能融合'),\n    ('about.html','通信–感知–计算–智能融合'),\n    ('en/index.html','integrated sensing, communication, computing, and intelligence'),\n    ('en/about.html','integrated sensing, communication, computing, and intelligence')\n]:\n    if required not in (ROOT/rel).read_text(encoding='utf-8'):\n        errors.append(f'{rel}: missing canonical PAI integration terminology')\n\n# Public pages need a stable social card, app icon metadata and a keyboard skip link.\nfor rel in paired:\n    for candidate in (rel,'en/'+rel):\n        p=ROOT/candidate\n        if not p.exists(): continue\n        text=p.read_text(encoding='utf-8')\n        for token,label in [\n            ('og:image','Open Graph image'),('apple-touch-icon','Apple touch icon'),\n            ('site.webmanifest','web manifest'),('class="skip-link"','skip link'),('id="main-content"','main landmark target')\n        ]:\n            if token not in text: errors.append(f'{candidate}: missing {label}')\nif not (ROOT/'assets/images/social/pai-share.png').exists(): errors.append('missing social share image')\nfor rel in ('assets/icons/favicon.svg','assets/icons/favicon-32.png','assets/icons/apple-touch-icon.png','assets/icons/icon-192.png','assets/icons/icon-512.png','site.webmanifest'):\n    if not (ROOT/rel).exists(): errors.append(f'missing brand asset: {rel}')\n'''
    # place before the final error reporting block
    idx=v.rfind("if errors:")
    if idx==-1: raise RuntimeError('validate.py final error block not found')
    v=v[:idx]+insert+'\n'+v[idx:]
val.write_text(v,encoding='utf-8')

print('site completeness polish applied')
