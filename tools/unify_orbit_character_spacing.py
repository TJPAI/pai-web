from pathlib import Path
import re

p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old="""        const charStep=ascii
          ? (chars.length<=4?5.0:Math.min(3.6,32/Math.max(1,chars.length-1)))
          : (chars.length<=2?7.8:7.6);"""
new="""        /* One fixed intra-label spacing rule per script. Menu length no longer
           changes character spacing; only the label's total arc width changes. */
        const charStep=ascii?3.6:7.6;"""
if old not in s:
    raise SystemExit('current charStep block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

for html in Path('.').rglob('*.html'):
    text=html.read_text(encoding='utf-8')
    text=re.sub(r'site\.js\?v=[^\"\']+','site.js?v=20260920-65',text)
    html.write_text(text,encoding='utf-8')
