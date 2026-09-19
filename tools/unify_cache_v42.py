from pathlib import Path
import re

for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'(assets/css/site\.css)(?:\?v=[^"\']+)?', r'\1?v=20260920-42', text)
    text=re.sub(r'(assets/js/site\.js)(?:\?v=[^"\']+)?', r'\1?v=20260920-42', text)
    path.write_text(text)
