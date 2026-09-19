from pathlib import Path
import re

js_path=Path('assets/js/site.js')
js=js_path.read_text()
old="""    const previewDocumentHeight=mainDocumentTop+previewMain.scrollHeight+(previewFooter?.scrollHeight||0);
    const previewMaxScroll=Math.max(0,previewDocumentHeight-innerHeight);
    const previewScroll=Math.min(targetScroll,previewMaxScroll);
"""
new="""    /* The preview must show the exact same saved Y that menu navigation requests.
       Do not independently clamp against preview geometry: applyPage is the single
       authority that clamps against the real destination document after handoff. */
    const previewScroll=targetScroll;
"""
if old not in js:
    raise SystemExit('preview clamp block not found')
js=js.replace(old,new,1)
js_path.write_text(js)

for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'(assets/js/site\.js)(?:\?v=[^\"\']+)?', r'\1?v=20260920-46', text)
    path.write_text(text)
