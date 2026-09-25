#!/usr/bin/env python3
"""Keep navigation script references identical in source previews and releases."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = 'assets/js/anchor-navigation.js?v=20260925-03'
check_only = '--check' in sys.argv
errors = []
changed = 0
for path in ROOT.rglob('*.html'):
    if 'geosketch-mvp' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    if '</body>' not in text:
        continue
    relative = path.relative_to(ROOT)
    prefix = '../' * len(relative.parent.parts)
    tag = f'<script src="{prefix}{SCRIPT}"></script>'
    refs = re.findall(r'<script\b[^>]*src=["\'][^"\']*(?:menu-exclusive|anchor-navigation)\.js[^"\']*["\'][^>]*></script>', text)
    if refs == [tag]:
        continue
    if check_only:
        errors.append(str(relative))
        continue
    for ref in refs:
        text = text.replace(ref, '')
    path.write_text(text.replace('</body>', tag + '</body>', 1), encoding='utf-8')
    changed += 1
if errors:
    sys.exit('Navigation scripts out of sync: ' + ', '.join(errors))
print('Navigation script references passed.' if check_only else f'Updated {changed} page(s).')
