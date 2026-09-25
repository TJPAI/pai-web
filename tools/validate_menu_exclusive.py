#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = 'assets/js/menu-exclusive.js?v=20260925-01'
errors = []

pattern = re.compile(r"<script\b[^>]*\bsrc=['\"]([^'\"]*menu-exclusive\.js(?:\?v=[^'\"]+)?)['\"][^>]*></script>", re.I)

for path in ROOT.rglob('*.html'):
    if 'geosketch-mvp' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    if '</body>' not in text:
        continue

    rel = path.relative_to(ROOT)
    depth = len(rel.parent.parts)
    expected = '../' * depth + SCRIPT
    refs = pattern.findall(text)

    if len(refs) != 1:
        errors.append(f'{rel}: expected exactly one menu-exclusive script; found {len(refs)}')
        continue
    if refs[0] != expected:
        errors.append(f'{rel}: menu-exclusive path is {refs[0]!r}; expected {expected!r}')

    if '/pai-web/assets/js/menu-exclusive.js' in text:
        errors.append(f'{rel}: contains hard-coded GitHub Pages /pai-web menu helper path')

if errors:
    print('Menu exclusivity deployment validation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

print('Menu exclusivity deployment validation passed.')
