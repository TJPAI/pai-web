from pathlib import Path
import re

js_path=Path('assets/js/site.js')
js=js_path.read_text()
old="""    previewMain.removeAttribute('id');
    previewMain.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));
"""
new="""    previewMain.removeAttribute('id');
    /* Preserve descendant section IDs in the swipe preview. About page mobile
       layout depends on #overview/#collaboration/#achievements/#international-impact;
       stripping them changes vertical geometry and causes a handoff jump. */
"""
if old not in js:
    raise SystemExit('preview descendant id stripping block not found')
js=js.replace(old,new,1)
js_path.write_text(js)

for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'(assets/js/site\\.js)(?:\\?v=[^\\"\\']+)?', r'\\1?v=20260920-48', text)
    path.write_text(text)
