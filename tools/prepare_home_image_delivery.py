#!/usr/bin/env python3
"""Re-encode the two large homepage WebP images for delivery without changing dimensions."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'assets' / 'images' / 'home'
QUALITY = 78
TARGETS = (
    'microsoft-indoor-localization-competition.webp',
    'ciie-navigation.webp',
)

for name in TARGETS:
    path = HOME / name
    if not path.is_file():
        raise SystemExit(f'missing homepage image: {path.relative_to(ROOT)}')
    before = path.stat().st_size
    with Image.open(path) as image:
        size = image.size
        image.convert('RGB').save(path, 'WEBP', quality=QUALITY, method=6)
    after = path.stat().st_size
    with Image.open(path) as check:
        if check.size != size:
            raise SystemExit(f'{name}: dimensions changed unexpectedly: {size} -> {check.size}')
    if after >= before:
        raise SystemExit(f'{name}: delivery re-encode did not reduce size ({before} -> {after})')
    print(f'{name}: {size[0]}x{size[1]}, {before} -> {after} bytes ({100*(before-after)/before:.1f}% smaller)')
