#!/usr/bin/env python3
from pathlib import Path
import re, subprocess
ROOT=Path(__file__).resolve().parents[1]

# 1) Make faculty detail minor headings explicit semantic typography.
for base in (ROOT/'people', ROOT/'en'/'people'):
    for p in base.glob('*.html'):
        text=p.read_text(encoding='utf-8')
        text=re.sub(r'(<section class="detail-block">\s*)<h3(?![^>]*class=)', r'\1<h3 class="title-minor"', text)
        p.write_text(text,encoding='utf-8')

# 2) Semantic classes become the sole typography selectors.
typ=ROOT/'assets/css/typography.css'
text=typ.read_text(encoding='utf-8')
repls={
'.title-display,.home-hero h1{':'.title-display{',
'.title-page,.page-hero h1{':'.title-page{',
'.title-section,.section-head h2,.join h2{':'.title-section{',
'.title-feature,.prose h2,.research-direction h2,.research h3,.research-title,.impact h3,.person-detail h2{':'.title-feature{',
'.title-item,.challenge h3,#collaboration .partner h3,#achievements .highlight h3,#international-impact .detail-block h3,.join-item h3,.team-grid .person h3,.pub h3,.news-row h3,.contact-card h3{':'.title-item{',
'.item-index,#achievements .highlight .num,.challenge .num,.join-item .num{':'.item-index{',
'.title-minor,.person-detail .detail-block h3{':'.title-minor{',
}
for old,new in repls.items():
    if old not in text:
        raise SystemExit(f'missing typography selector: {old}')
    text=text.replace(old,new)
typ.write_text(text,encoding='utf-8')

# 3) Strengthen CI contracts and disallow structural fallbacks in typography.css.
val=ROOT/'tools/validate.py'
v=val.read_text(encoding='utf-8')
needle="for required in ('--title-display-size','--title-page-size','--title-section-size','--title-feature-size','--title-item-size','--title-minor-size','.research-title'):\n    if required not in _typography:\n        errors.append(f'assets/css/typography.css: missing canonical title contract {required}')\n"
addition=needle+"\n# Semantic title classes are the canonical presentation contract; typography.css must not depend on page structure.\nfor required in ('.title-display{','.title-page{','.title-section{','.title-feature{','.title-item{','.title-minor{','.item-index{'):\n    if required not in _typography:\n        errors.append(f'assets/css/typography.css: missing semantic rule {required}')\nfor banned in ('.home-hero h1','.page-hero h1','.section-head h2','.research h3','.partner h3','.highlight h3','.person-detail .detail-block h3'):\n    if banned in _typography:\n        errors.append(f'assets/css/typography.css: structural fallback remains ({banned}); use semantic title classes')\n\n# Faculty detail minor headings must declare their semantic level explicitly.\nfor base in (ROOT/'people',ROOT/'en'/'people'):\n    for html in base.glob('*.html'):\n        text=html.read_text(encoding='utf-8')\n        for attrs,inner in re.findall(r'<section\\b([^>]*)class=[\"\\\'][^\"\\\']*\\bdetail-block\\b[^\"\\\']*[\"\\\'][^>]*>(.*?)</section>',text,re.I|re.S):\n            m=re.search(r'<h3\\b([^>]*)>',inner,re.I)\n            if m and 'title-minor' not in m.group(1):\n                errors.append(f'{html.relative_to(ROOT)}: detail-block h3 must use title-minor')\n"
if needle not in v:
    raise SystemExit('validator insertion point missing')
v=v.replace(needle,addition,1)
val.write_text(v,encoding='utf-8')

# Clean temporary machinery before commit.
(ROOT/'.github/workflows/finalize-semantic-typography.yml').unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)

subprocess.run(['python','tools/validate.py'],cwd=ROOT,check=True)
subprocess.run(['node','--check','assets/js/site.js'],cwd=ROOT,check=True)
subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=ROOT,check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=ROOT,check=True)
subprocess.run(['git','add','-A'],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','refactor: finalize semantic typography ownership'],cwd=ROOT,check=True)
subprocess.run(['git','push'],cwd=ROOT,check=True)
