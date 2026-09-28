#!/usr/bin/env python3
"""Reject insecure HTTP links in public HTML documents."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', 'node_modules', 'templates', 'tmp', 'geosketch-mvp', '_site'}
errors = []
checked = 0

for path in sorted(ROOT.rglob('*.html')):
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED for part in rel.parts):
        continue
    checked += 1
    text = path.read_text(encoding='utf-8')
    for tag in re.findall(r'<a\b[^>]*>', text, re.I):
        match = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.I)
        if match and match.group(1).lower().startswith('http://'):
            errors.append(f'{rel}: insecure public link {match.group(1)}')

if errors:
    print('Secure-link validation failed:')
    for error in errors:
        print(' -', error)
    sys.exit(1)

print(f'Secure-link validation passed on {checked} HTML page(s).')
