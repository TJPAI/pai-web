#!/usr/bin/env python3
"""Use the committed full-logo social card on every bilingual content page."""
import re
from site_config import ROOT, BASE_URL

SHARE_IMAGE = BASE_URL + 'assets/images/social/pai-share-v4.jpg?v=20260929-logo-new'
asset = ROOT / 'assets/images/social/pai-share-v4.jpg'
if not asset.is_file() or not asset.read_bytes().startswith(b'\xff\xd8\xff'):
    raise SystemExit('The committed social card must be a real JPEG')
changed = 0
for path in ROOT.rglob('*.html'):
    if 'geosketch-mvp' in path.parts or '_site' in path.parts or path.name == '404.html':
        continue
    text = path.read_text(encoding='utf-8')
    if 'class="site-header"' not in text:
        continue
    updated = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]+(">)',
                     lambda m: m[1] + SHARE_IMAGE + m[2], text)
    for dimension, value in (('width', 1200), ('height', 630)):
        updated = re.sub(rf'(<meta property="og:image:{dimension}" content=")\d+(">)',
                         lambda m: m[1] + str(value) + m[2], updated)
    updated = updated.replace('<meta name="twitter:card" content="summary">',
                              '<meta name="twitter:card" content="summary_large_image">')
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1
print(f'Prepared full-logo social metadata in {changed} HTML file(s); image={SHARE_IMAGE}')
