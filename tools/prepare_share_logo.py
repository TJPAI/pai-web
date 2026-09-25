#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_IMAGE = 'https://tjpai.github.io/pai-web/assets/images/social/pai-share-v4.jpg'
NEW_IMAGE = 'https://tjpai.github.io/pai-web/assets/icons/icon-512.png'

changed = 0
for path in ROOT.rglob('*.html'):
    if 'geosketch-mvp' in path.parts or path.name == '404.html':
        continue
    text = path.read_text(encoding='utf-8')
    if 'class="site-header"' not in text:
        continue
    updated = text.replace(OLD_IMAGE, NEW_IMAGE)
    updated = updated.replace('<meta property="og:image:width" content="1200">', '<meta property="og:image:width" content="512">')
    updated = updated.replace('<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="512">')
    updated = updated.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary">')
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

print(f'Prepared logo share metadata in {changed} HTML file(s).')
