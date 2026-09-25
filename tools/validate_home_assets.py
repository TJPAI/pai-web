#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

assets = (
    'microsoft-indoor-localization-competition.webp',
    'ciie-navigation.webp',
    'datong-mine-magnetic-communication.webp',
)

pages = {
    'index.html': (ROOT / 'index.html', 'assets/images/home/'),
    'en/index.html': (ROOT / 'en/index.html', '../assets/images/home/'),
}

for asset in assets:
    if not (ROOT / 'assets/images/home' / asset).is_file():
        errors.append(f'assets/images/home/{asset}: missing homepage achievement image')

for rel, (path, prefix) in pages.items():
    text = path.read_text(encoding='utf-8')
    for asset in assets:
        src = prefix + asset
        matches = re.findall(rf'<img\b[^>]*\bsrc=["\']{re.escape(src)}["\'][^>]*>', text, re.I)
        if len(matches) != 1:
            errors.append(f'{rel}: expected exactly one homepage image reference to {src}; found {len(matches)}')
            continue
        tag = matches[0]
        if not re.search(r'\bloading=["\']eager["\']', tag, re.I):
            errors.append(f'{rel}: {asset} must be loading="eager" to avoid Safari re-entry flash')
        if not re.search(r'\bdecoding=["\']sync["\']', tag, re.I):
            errors.append(f'{rel}: {asset} must be decoding="sync" to avoid Safari re-entry flash')

if errors:
    print('Homepage asset validation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

print('Homepage asset validation passed.')
