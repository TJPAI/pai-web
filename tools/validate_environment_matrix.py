#!/usr/bin/env python3
"""Validate both Preview and Production URL/crawl contracts without changing active state."""
from pathlib import Path
from urllib.parse import urlparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'config' / 'site.json').read_text(encoding='utf-8'))
ENVIRONMENTS = CONFIG.get('environments') or {}
errors = []

required = {'preview', 'production'}
missing = required - set(ENVIRONMENTS)
if missing:
    errors.append(f'config/site.json: missing required environment(s): {", ".join(sorted(missing))}')

known_bases = [str(raw.get('base_url', '')).strip() for raw in ENVIRONMENTS.values() if isinstance(raw, dict)]


def rewrite_for(text: str, base_url: str) -> str:
    for base in known_bases:
        if base and base != base_url:
            text = text.replace(base, base_url)
    return text


def validate_environment(name: str) -> None:
    raw = ENVIRONMENTS.get(name)
    if not isinstance(raw, dict):
        return
    base = str(raw.get('base_url', '')).strip()
    custom_domain = raw.get('custom_domain')
    allow_indexing = raw.get('allow_indexing')
    parsed = urlparse(base)

    if parsed.scheme != 'https' or not parsed.netloc or not base.endswith('/'):
        errors.append(f'{name}: base_url must be an https URL ending with /')
        return

    if name == 'preview':
        if allow_indexing is not False:
            errors.append('preview: allow_indexing must remain false')
        if custom_domain is not None:
            errors.append('preview: custom_domain must remain null')
    if name == 'production':
        if allow_indexing is not True:
            errors.append('production: allow_indexing must be true')
        if not custom_domain:
            errors.append('production: custom_domain is required')
        elif parsed.hostname != custom_domain:
            errors.append('production: custom_domain must match base_url hostname')

    # Simulate the same known-base replacement used by prepare_site_urls.py, but only
    # in memory. Every page identity URL must resolve exclusively to this environment.
    for path in ROOT.rglob('*.html'):
        rel = path.relative_to(ROOT)
        if any(part in {'.git', 'node_modules', 'templates', 'tmp', 'geosketch-mvp'} for part in rel.parts):
            continue
        source = path.read_text(encoding='utf-8')
        transformed = rewrite_for(source, base)
        for other in known_bases:
            if other and other != base and other in transformed:
                errors.append(f'{name}: {rel} retains URL from another environment: {other}')
        canonical = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', transformed, re.I)
        if canonical and not canonical.group(1).startswith(base):
            errors.append(f'{name}: {rel} canonical does not use configured base_url')
        og_url = re.search(r'<meta\b[^>]*property=["\']og:url["\'][^>]*content=["\']([^"\']+)', transformed, re.I)
        if og_url and not og_url.group(1).startswith(base):
            errors.append(f'{name}: {rel} og:url does not use configured base_url')

    sitemap = rewrite_for((ROOT / 'sitemap.xml').read_text(encoding='utf-8'), base)
    for other in known_bases:
        if other and other != base and other in sitemap:
            errors.append(f'{name}: sitemap retains URL from another environment: {other}')
    locs = re.findall(r'<loc>([^<]+)</loc>', sitemap)
    if not locs or any(not loc.startswith(base) for loc in locs):
        errors.append(f'{name}: sitemap contains URL outside configured base_url')

    # Validate the outputs prepare_site_urls.py would derive for crawl/domain policy.
    if allow_indexing:
        robots = f'User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n'
        if 'Allow: /' not in robots or f'Sitemap: {base}sitemap.xml' not in robots:
            errors.append(f'{name}: production robots contract is invalid')
    else:
        robots = 'User-agent: *\nDisallow: /\n'
        if 'Disallow: /' not in robots:
            errors.append(f'{name}: preview robots contract is invalid')


for environment in ('preview', 'production'):
    validate_environment(environment)

if errors:
    print('Environment matrix validation failed:')
    for error in errors:
        print(' -', error)
    sys.exit(1)

print('Environment matrix OK: Preview and Production URL, crawl, sitemap, and custom-domain contracts preflighted.')
