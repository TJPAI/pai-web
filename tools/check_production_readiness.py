#!/usr/bin/env python3
"""Check production prerequisites that are not ordinary Preview-source state.

Generated production URLs/robots/sitemap/CNAME are owned by prepare_site_urls.py and
validate_seo_contracts.py after the environment switch. This check therefore validates
the selected production configuration plus source invariants that must survive cutover.
"""
from pathlib import Path
import json
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
errors = []

config_path = ROOT / 'config' / 'site.json'
try:
    config = json.loads(config_path.read_text(encoding='utf-8'))
except Exception as exc:
    raise SystemExit(f'config/site.json is invalid: {exc}')

active = config.get('active_environment')
environments = config.get('environments') or {}
production = environments.get('production') or {}
preview = environments.get('preview') or {}

if active != 'production':
    errors.append('config/site.json active_environment is not production')

base_url = str(production.get('base_url') or '')
parsed = urlparse(base_url)
if parsed.scheme != 'https' or parsed.netloc != 'ai.tongji.edu.cn' or parsed.path != '/':
    errors.append('production base_url must be https://ai.tongji.edu.cn/')
if production.get('custom_domain') != 'ai.tongji.edu.cn':
    errors.append('production custom_domain must be ai.tongji.edu.cn')
if production.get('allow_indexing') is not True:
    errors.append('production allow_indexing must be true')
if preview.get('allow_indexing') is not False:
    errors.append('preview allow_indexing must remain false')
if preview.get('base_url') == production.get('base_url'):
    errors.append('preview and production base_url must remain distinct')

# Temporary external faculty imagery must never return to the source tree.
for html in ROOT.rglob('*.html'):
    rel = html.relative_to(ROOT)
    if 'geosketch-mvp' in rel.parts:
        continue
    text = html.read_text(encoding='utf-8')
    if 'https://ai.tongji.edu.cn/new_web/image/' in text:
        errors.append(f'{rel}: still depends on temporary-site faculty image URLs')

# Publication PDFs are intentionally not maintained in this repository.
for rel in ('data/publications.json', 'data/publications-archive.json'):
    text = (ROOT / rel).read_text(encoding='utf-8')
    if '"pdf"' in text:
        errors.append(f'{rel}: contains a forbidden publication PDF field')

# Production must preserve the Safari-safe homepage image contract.
for rel in ('index.html', 'en/index.html'):
    text = (ROOT / rel).read_text(encoding='utf-8')
    for match in re.findall(r'<img\b[^>]*assets/images/home/[^>]+>', text, re.I):
        if not re.search(r'\bloading=["\']eager["\']', match, re.I):
            errors.append(f'{rel}: homepage image is not eager-loaded')
        if not re.search(r'\bdecoding=["\']sync["\']', match, re.I):
            errors.append(f'{rel}: homepage image is not synchronously decoded')

# Production-facing local assets that must exist before DNS cutover.
for rel in (
    'assets/images/brand/pai-logo.svg',
    'assets/images/social/pai-logo-share.png',
    'assets/icons/favicon.svg',
    'assets/icons/favicon-32.png',
    'assets/icons/apple-touch-icon.png',
    'assets/icons/icon-192.png',
    'assets/icons/icon-512.png',
    '404.html',
):
    if not (ROOT / rel).is_file():
        errors.append(f'{rel}: required production asset is missing')

if errors:
    print('Production readiness check FAILED:')
    for error in errors:
        print('ERROR:', error)
    sys.exit(1)

print('Production readiness source/config prerequisites passed.')
print('Next: run prepare_site_urls.py and validate_seo_contracts.py, then verify DNS, HTTPS and GitHub Pages Custom domain externally.')
