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
        errors.append(
            f'{source.relative_to(SITE)}: root-relative reference is not portable to the Preview subpath: {raw}'
        )
        return None
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
    if css.name == 'refine-bundle.css' and re.search(r'^\s*@import\b', text, re.M):
        errors.append('refine-bundle.css: unresolved @import in deployed bundle')
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
    'assets/images/social/pai-share-v4.jpg',
    'assets/js/site.js',
):
    if not (SITE / rel).exists():
        errors.append(f'missing required public artifact file: {rel}')

# GeoSketch is intentionally public-by-URL but excluded from institutional search indexing.
geosketch = SITE / 'geosketch-mvp' / 'index.html'
if not geosketch.is_file():
    errors.append('missing required public artifact file: geosketch-mvp/index.html')
else:
    geosketch_text = geosketch.read_text(encoding='utf-8')
    if '<meta name="robots" content="noindex,nofollow">' not in geosketch_text:
        errors.append('geosketch-mvp/index.html: deployed utility must remain noindex,nofollow')

# Runtime safety/privacy/accessibility contracts must be true in the final JS users receive.
site_js_path = SITE / 'assets/js/site.js'
if site_js_path.is_file():
    site_js = site_js_path.read_text(encoding='utf-8')

    # Never unregister unrelated Service Workers sharing the production origin.
    scoped_cleanup = "rs.filter(r=>r.scope===legacyScope).map(r=>r.unregister())"
    unsafe_cleanup = "rs.map(r=>r.unregister())"
    if scoped_cleanup not in site_js:
        errors.append('assets/js/site.js: deployed legacy Service Worker cleanup is not scope-limited')
    if unsafe_cleanup in site_js:
        errors.append('assets/js/site.js: deployed runtime still contains origin-wide Service Worker unregister')

    # DOI links are generated at runtime, so the static HTML validator cannot see them.
    safe_doi_link = 'target="_blank" rel="noopener noreferrer">DOI ↗</a>'
    unsafe_doi_link = 'target="_blank" rel="noopener">DOI ↗</a>'
    if safe_doi_link not in site_js:
        errors.append('assets/js/site.js: runtime DOI links are missing noopener+noreferrer')
    if unsafe_doi_link in site_js:
        errors.append('assets/js/site.js: runtime DOI links still expose referrer information')

    # Closed orbit navigation is invisible, so its links must stay out of the focus tree.
    orbit_contracts = (
        ("wheel.setAttribute('aria-hidden',open?'false':'true')", 'deployed orbit does not expose open/closed state to assistive technology'),
        ("link.setAttribute('tabindex','-1')", 'closed orbit links remain keyboard-focusable'),
        ("link.removeAttribute('tabindex')", 'open orbit links do not restore keyboard focusability'),
        ("syncOrbitA11y(false)", 'orbit is not initialized in the hidden/non-focusable state'),
        ("if(link.closest('.pai-orbit-wheel')) closeOrbitMenu()", 'orbit selection does not close the quick menu before navigation'),
        ("const orbit=document.querySelector('.pai-orbit.open')", 'Escape handling does not detect an open orbit'),
        ("orbit.querySelector('.pai-orbit-toggle')?.focus()", 'Escape handling does not restore focus to the orbit toggle'),
    )
    for snippet, message in orbit_contracts:
        if snippet not in site_js:
            errors.append(f'assets/js/site.js: {message}')

if errors:
    print('Public artifact validation failed:')
    for error in errors:
        print(' -', error)
    sys.exit(1)

files = sum(1 for path in SITE.rglob('*') if path.is_file())
print(f'Public artifact validation passed: {files} files; local references resolve, Preview paths are portable, GeoSketch stays noindex, and runtime SW/DOI/orbit safety contracts hold.')
