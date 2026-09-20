from pathlib import Path
import re

NEW='20260920-60'
count=0
for p in Path('.').rglob('*.html'):
    s=p.read_text(encoding='utf-8')
    ns=re.sub(r'site\.js\?v=[^"\']+', f'site.js?v={NEW}', s)
    if ns!=s:
        p.write_text(ns,encoding='utf-8')
        count+=1
print(f'updated {count} html files')
if count==0:
    raise SystemExit('no site.js cache tokens updated')
