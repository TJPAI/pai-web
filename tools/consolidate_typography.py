#!/usr/bin/env python3
from pathlib import Path
import re

css_files=[Path('assets/css/site.css'),Path('assets/css/refine-base.css'),Path('assets/css/app-core.css')]
typography_props={'font-size','font-weight','color','line-height','letter-spacing','text-transform'}
selectors=[
    '.eyebrow','.hero h1','.home-hero h1','.page-hero h1',
    '.section-head h2','.content-section h2','.prose h2','.join h2',
    '.challenge h3','.research h3','.impact h3','.challenge h3,.research h3,.impact h3',
    '.partner h3','.home-hero~.section .partner h3','.highlight h3','.news-row h3',
    '.person h3','.team-grid .person h3','.pub h3','.contact-card h3','.join-item h3',
    '.person-detail h2','.detail-block h3','.person-detail .detail-block h3',
    '.research-direction h2','.research-title',
    '#collaboration .partner h3,#achievements .highlight h3,#international-impact .detail-block h3',
    '.challenge .num','.highlight .num','.join-item .num'
]

def strip_typography(body):
    kept=[]
    for raw in body.split(';'):
        if not raw.strip():
            continue
        if ':' not in raw:
            kept.append(raw.strip())
            continue
        prop=raw.split(':',1)[0].strip().lower()
        if prop in typography_props:
            continue
        kept.append(raw.strip())
    return ';'.join(kept)

for path in css_files:
    text=path.read_text(encoding='utf-8')
    before=text
    for selector in selectors:
        pat=re.compile(re.escape(selector)+r'\{([^{}]*)\}')
        text=pat.sub(lambda m,s=selector:s+'{'+strip_typography(m.group(1))+'}',text)
    path.write_text(text,encoding='utf-8')
    print(path, 'changed' if text!=before else 'unchanged')

typo=Path('assets/css/typography.css')
t=typo.read_text(encoding='utf-8')
old='.prose h2,.research-direction h2,.research h3,.impact h3,.person-detail h2{'
new='.prose h2,.research-direction h2,.research h3,.research-title,.impact h3,.person-detail h2{'
if old in t:
    t=t.replace(old,new,1)
typo.write_text(t,encoding='utf-8')

validate=Path('tools/validate.py')
v=validate.read_text(encoding='utf-8')
marker='# Canonical typography ownership guardrail.'
if marker not in v:
    guard='''\n\n# Canonical typography ownership guardrail.\n# Title visual properties belong only in assets/css/typography.css; component layers may keep layout properties.\n_typography_owned_selectors=[\n    '.eyebrow','.hero h1','.home-hero h1','.page-hero h1',\n    '.section-head h2','.content-section h2','.prose h2','.join h2',\n    '.challenge h3','.research h3','.research-title','.impact h3','.partner h3','.highlight h3','.news-row h3',\n    '.person h3','.team-grid .person h3','.pub h3','.contact-card h3','.join-item h3',\n    '.person-detail h2','.detail-block h3','.person-detail .detail-block h3','.research-direction h2',\n    '.challenge .num','.highlight .num','.join-item .num'\n]\n_typography_owned_props={'font-size','font-weight','color','line-height','letter-spacing','text-transform'}\nfor rel in ('assets/css/site.css','assets/css/refine-base.css','assets/css/app-core.css'):\n    css=(ROOT/rel).read_text(encoding='utf-8')\n    for match in re.finditer(r'([^{}]+)\\{([^{}]*)\\}',css):\n        selector=match.group(1).strip()\n        if not any(token in selector for token in _typography_owned_selectors):\n            continue\n        props={part.split(':',1)[0].strip().lower() for part in match.group(2).split(';') if ':' in part}\n        bad=sorted(props&_typography_owned_props)\n        if bad:\n            errors.append(f'{rel}: canonical title typography leaked into "{selector}" ({", ".join(bad)}); use typography.css')\n\n_typography=(ROOT/'assets/css/typography.css').read_text(encoding='utf-8')\nfor required in ('--title-display-size','--title-page-size','--title-section-size','--title-feature-size','--title-item-size','--title-minor-size','.research-title'):\n    if required not in _typography:\n        errors.append(f'assets/css/typography.css: missing canonical title contract {required}')\n'''
    anchor='if errors:\n'
    pos=v.rfind(anchor)
    v=(v[:pos]+guard+'\n'+v[pos:]) if pos!=-1 else (v+guard)
    validate.write_text(v,encoding='utf-8')
