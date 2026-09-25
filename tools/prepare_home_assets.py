#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
assets = (
    'microsoft-indoor-localization-competition.webp',
    'ciie-navigation.webp',
    'datong-mine-magnetic-communication.webp',
)
pages = {
    'index.html': (ROOT / 'index.html', 'assets/images/home/'),
    'en/index.html': (ROOT / 'en/index.html', '../assets/images/home/'),
}

errors = []
changed = 0
for rel, (path, prefix) in pages.items():
    text = path.read_text(encoding='utf-8')
    original = text
    for asset in assets:
        src = re.escape(prefix + asset)
        pattern = re.compile(rf'(<img\b[^>]*\bsrc=["\']{src}["\'][^>]*?)\s+loading=["\']lazy["\']\s+decoding=["\']async["\']([^>]*>)', re.I)
        text, count = pattern.subn(r'\1 loading="eager" decoding="sync"\2', text, count=1)
        if count != 1:
            canonical = re.findall(rf'<img\b[^>]*\bsrc=["\']{src}["\'][^>]*\bloading=["\']eager["\'][^>]*\bdecoding=["\']sync["\'][^>]*>', text, re.I)
            if len(canonical) != 1:
                errors.append(f'{rel}: could not confirm Safari-safe eager/sync for {asset}')
    if text != original:
        path.write_text(text, encoding='utf-8')
        changed += 1

if errors:
    print('Homepage image preparation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

if changed:
    print(f'Canonicalized homepage images for Safari ({changed} page(s) changed).')
else:
    print('Homepage images already Safari-safe in source; no deployment rewrite needed.')
