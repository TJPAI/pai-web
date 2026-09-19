from pathlib import Path
import re

css = Path('assets/css/site.css')
text = css.read_text()
marker = '/* TEMP v36: hide footer for swipe visual test */'
rule = f'\n{marker}\n.site-footer{{display:none!important}}\n'
if marker not in text:
    text += rule
css.write_text(text)

for p in Path('.').rglob('*.html'):
    s = p.read_text()
    s2 = re.sub(r'site\.css\?v=[^"\']+', 'site.css?v=20260919-36', s)
    if s2 != s:
        p.write_text(s2)
