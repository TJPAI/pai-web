#!/usr/bin/env python3
from pathlib import Path
import re
VERSION='20260919-6'
changed=[]
for path in Path('.').rglob('*.html'):
    if '.git' in path.parts:
        continue
    text=path.read_text(encoding='utf-8')
    original=text
    text=re.sub(r'(href=["\'](?:\.\./)*assets/css/site\.css)(?:\?v=[^"\']+)?(["\'])', rf'\1?v={VERSION}\2', text)
    text=re.sub(r'(href=["\'](?:\.\./)*assets/css/refine\.css)(?:\?v=[^"\']+)?(["\'])', rf'\1?v={VERSION}\2', text)
    if text!=original:
        path.write_text(text,encoding='utf-8')
        changed.append(str(path))
refine=Path('assets/css/refine.css')
text=refine.read_text(encoding='utf-8')
original=text
for name in ('refine-base.css','app-core.css','typography.css'):
    text=re.sub(rf'({re.escape(name)})\?v=[^)"\']+', rf'\1?v={VERSION}', text)
if text==original:
    raise SystemExit('refine.css imports were not updated')
refine.write_text(text,encoding='utf-8')
if not changed:
    raise SystemExit('no HTML stylesheet references updated')
print(f'updated {len(changed)} HTML files to cache version {VERSION}')
