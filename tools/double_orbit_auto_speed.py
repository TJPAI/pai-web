from pathlib import Path
import re

p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old='const AUTO_DEG_PER_SECOND=3;'
new='const AUTO_DEG_PER_SECOND=6;'
if old not in s:
    raise SystemExit('AUTO_DEG_PER_SECOND=3 not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

for html in Path('.').rglob('*.html'):
    t=html.read_text(encoding='utf-8')
    t=re.sub(r'site\.js\?v=[^\"\']+','site.js?v=20260920-69',t)
    html.write_text(t,encoding='utf-8')
