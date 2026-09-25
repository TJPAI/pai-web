#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
changed = 0

for path in (ROOT / 'en').rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    updated = text.replace('>Publications</a>', '>Outputs</a>')
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

print(f'Prepared Outputs labels in {changed} English page(s).')
