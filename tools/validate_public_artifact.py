#!/usr/bin/env python3
"""Validate the final staged Pages tree before upload."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
errors = []

if not SITE.is_dir():
    raise SystemExit('_site is missing; run prepare_public_artifact.py first')


def resolve_local(source: Path, raw: str) -> Path | None:
    raw = raw.strip()
    if not raw or raw.startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:')):
        return None
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    if path.startswith('/'):
        # Site source uses relative URLs for runtime assets; root-relative paths in
        # public documents are interpreted from the staged site root.
        target = SITE / path.lstrip('/')
    else:
        target = source.parent / path
    try:
        target = target.resolve()
        target.relative_to(SITE.resolve())
    except Exception:
        errors.append(f'{source.relative_to(SITE)}: reference escapes public artifact: {raw}')
        return None
    return target


for html in SITE.rglob('*.html'):
    text = html.read_text(encoding='utf-8')
    for attr, raw in re.findall(r'\b(src|href)=["\']([^"\']+)["\']', text, re.I):
        target = resolve_local(html, raw)
        if target is not None and not target.exists():
            errors.append(f'{html.relative_to(SITE)}: missing local {attr} target {raw}')

for css in SITE.rglob('*.css'):
    text = css.read_text(encoding='utf-8')
    for raw in re.findall(r'url\(\s*["\']?([^"\')]+)', text, re.I):
        target = resolve_local(css, raw)
        if target is not None and not target.exists():
            errors.append(f'{css.relative_to(SITE)}: missing CSS url() target {raw}')

manifest_path = SITE / 'site.webmanifest'
try:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for icon in manifest.get('icons', []):
        raw = icon.get('src', '')
        target = resolve_local(manifest_path, raw)
        if target is not None and not target.exists():
            errors.append(f'site.webmanifest: missing icon target {raw}')
except Exception as exc:
    errors.append(f'site.webmanifest: invalid JSON: {exc}')

# Deployment-only outputs must be present after all transforms.
for rel in (
    'index.html', 'en/index.html', '404.html', 'robots.txt', 'sitemap.xml',
    'site.webmanifest', 'sw.js', 'assets/css/refine-bundle.css',
    'assets/images/social/pai-logo-share.png', 'assets/js/site.js',
):
    if not (SITE / rel).exists():
        errors.append(f'missing required public artifact file: {rel}')

if errors:
    print('Public artifact validation failed:')
    for error in errors:
        print(' -', error)
    sys.exit(1)

files = sum(1 for path in SITE.rglob('*') if path.is_file())
print(f'Public artifact validation passed: {files} files; local HTML/CSS/manifest references resolve.')
