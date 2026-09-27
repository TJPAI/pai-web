#!/usr/bin/env python3
"""Validate the web manifest and PNG icon dimensions without external packages."""
from pathlib import Path
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
manifest_path = ROOT / 'site.webmanifest'

try:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
except Exception as exc:
    raise SystemExit(f'site.webmanifest: invalid JSON: {exc}')

for key in ('name', 'short_name', 'id', 'start_url', 'scope', 'display', 'background_color', 'theme_color', 'icons'):
    if not manifest.get(key):
        errors.append(f'site.webmanifest: missing {key}')

for key in ('id', 'start_url', 'scope'):
    value = str(manifest.get(key, ''))
    if not value.startswith('./'):
        errors.append(f'site.webmanifest: {key} must stay relative for preview/custom-domain portability')

if manifest.get('display') != 'standalone':
    errors.append('site.webmanifest: display must remain standalone')


def png_size(path: Path):
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        return None
    return struct.unpack('>II', data[16:24])

expected_manifest_icons = {
    'assets/icons/icon-192.png': (192, 192),
    'assets/icons/icon-512.png': (512, 512),
}
seen = {}
for icon in manifest.get('icons', []):
    src = icon.get('src')
    if not src:
        errors.append('site.webmanifest: icon missing src')
        continue
    path = ROOT / src
    if not path.is_file():
        errors.append(f'site.webmanifest: missing icon file {src}')
        continue
    size = png_size(path)
    if size is None:
        errors.append(f'{src}: expected PNG icon')
        continue
    seen[src] = size
    declared = icon.get('sizes')
    if declared != f'{size[0]}x{size[1]}':
        errors.append(f'{src}: manifest sizes={declared!r} does not match PNG {size[0]}x{size[1]}')

for src, expected in expected_manifest_icons.items():
    if seen.get(src) != expected:
        errors.append(f'{src}: expected manifest icon dimensions {expected[0]}x{expected[1]}')

for src, expected in {
    'assets/icons/favicon-32.png': (32, 32),
    'assets/icons/apple-touch-icon.png': (180, 180),
}.items():
    path = ROOT / src
    if not path.is_file():
        errors.append(f'{src}: missing')
        continue
    size = png_size(path)
    if size != expected:
        errors.append(f'{src}: expected {expected[0]}x{expected[1]}, found {size}')

if errors:
    print('Manifest/icon validation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

print('Manifest/icon validation passed.')
