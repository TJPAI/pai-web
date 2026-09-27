#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
import xml.etree.ElementTree as ET

from site_config import ROOT, BASE_URL, CUSTOM_DOMAIN, ALLOW_INDEXING, ENVIRONMENT

errors = []

# Canonical bilingual content pages expected to be indexable at production cutover.
paired = [
    'index.html','about.html','research.html','team.html','publications.html','join.html','contact.html',
    'people/erwu-liu.html','people/rui-wang.html','people/gang-shen.html','people/dunhui-xiao.html',
    'people/shuyan-hu.html','people/yan-liu.html'
]

def public_url(rel):
    if rel == 'index.html':
        return BASE_URL
    if rel == 'en/index.html':
        return BASE_URL + 'en/'
    return BASE_URL + rel

expected = set()
for rel in paired:
    expected.add(public_url(rel))
    expected.add(public_url('en/' + rel))

# Sitemap must cover every canonical bilingual page exactly once and no stale content pages.
sitemap = ROOT / 'sitemap.xml'
try:
    tree = ET.parse(sitemap)
    ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    locs = [node.text.strip() for node in tree.findall('.//sm:loc', ns) if node.text]
except Exception as exc:
    errors.append(f'sitemap.xml: invalid XML: {exc}')
    locs = []

if len(locs) != len(set(locs)):
    errors.append('sitemap.xml: duplicate <loc> entries')
actual = set(locs)
for url in sorted(expected - actual):
    errors.append(f'sitemap.xml: missing canonical page {url}')
for url in sorted(actual - expected):
    errors.append(f'sitemap.xml: unexpected/stale canonical page {url}')

# Structured data contracts: both homepages identify the same research organization.
for rel in ('index.html', 'en/index.html'):
    text = (ROOT / rel).read_text(encoding='utf-8')
    m = re.search(r'<script type="application/ld\+json" data-pai-schema>(.*?)</script>', text, re.S)
    if not m:
        errors.append(f'{rel}: missing organization JSON-LD')
        continue
    try:
        data = json.loads(m.group(1))
    except Exception as exc:
        errors.append(f'{rel}: invalid organization JSON-LD: {exc}')
        continue
    if data.get('@type') != 'ResearchOrganization':
        errors.append(f'{rel}: JSON-LD @type must be ResearchOrganization')
    if data.get('name') != 'PAI Research Center':
        errors.append(f'{rel}: JSON-LD organization name drifted')
    if data.get('url') != BASE_URL:
        errors.append(f'{rel}: JSON-LD organization URL must be {BASE_URL}')
    if data.get('@id') != BASE_URL + '#organization':
        errors.append(f'{rel}: JSON-LD organization @id must use configured base URL')
    if not data.get('email'):
        errors.append(f'{rel}: JSON-LD organization email missing')

# Every faculty detail page must expose Person JSON-LD tied to the PAI organization.
for prefix in ('', 'en/'):
    for rel in paired[7:]:
        page = prefix + rel
        text = (ROOT / page).read_text(encoding='utf-8')
        m = re.search(r'<script type="application/ld\+json" data-pai-schema>(.*?)</script>', text, re.S)
        if not m:
            errors.append(f'{page}: missing Person JSON-LD')
            continue
        try:
            data = json.loads(m.group(1))
        except Exception as exc:
            errors.append(f'{page}: invalid Person JSON-LD: {exc}')
            continue
        if data.get('@type') != 'Person':
            errors.append(f'{page}: JSON-LD @type must be Person')
        if not data.get('name') or not data.get('jobTitle'):
            errors.append(f'{page}: JSON-LD name/jobTitle missing')
        member = data.get('memberOf') or {}
        if member.get('@id') != BASE_URL + '#organization':
            errors.append(f'{page}: JSON-LD memberOf must reference PAI organization')
        if data.get('url') != public_url(page):
            errors.append(f'{page}: JSON-LD url does not match canonical page URL')
        expected_id = public_url(page) + '#person'
        if data.get('@id') != expected_id:
            errors.append(f'{page}: JSON-LD @id must be {expected_id}')

# Crawl and custom-domain contracts are generated from the active environment.
robots = (ROOT / 'robots.txt').read_text(encoding='utf-8')
if ALLOW_INDEXING:
    if 'Disallow: /' in robots or 'Allow: /' not in robots:
        errors.append('robots.txt: indexing should be enabled for active environment')
    if f'Sitemap: {BASE_URL}sitemap.xml' not in robots:
        errors.append('robots.txt: production sitemap URL missing')
else:
    if 'Disallow: /' not in robots:
        errors.append('robots.txt: preview indexing must remain disabled')

cname = ROOT / 'CNAME'
if CUSTOM_DOMAIN:
    if not cname.is_file() or cname.read_text(encoding='utf-8').strip() != CUSTOM_DOMAIN:
        errors.append(f'CNAME: expected configured custom domain {CUSTOM_DOMAIN}')
elif cname.exists():
    errors.append('CNAME: must not exist when active environment has no custom domain')

if errors:
    print('SEO contract validation failed:')
    for error in errors:
        print(' -', error)
    sys.exit(1)

print(
    f'SEO contracts OK: env={ENVIRONMENT}; {len(expected)} sitemap URLs; '
    f'organization + faculty JSON-LD validated; indexing={"on" if ALLOW_INDEXING else "off"}'
)
