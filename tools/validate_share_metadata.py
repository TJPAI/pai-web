#!/usr/bin/env python3
from pathlib import Path
import re, sys

from site_config import ROOT, BASE_URL

SHARE_IMAGE = BASE_URL + 'assets/images/social/pai-share-v4.jpg?v=20260929-logo-new'
errors = []
checked = []


def meta_content(text, kind, key):
    for tag in re.findall(r'<meta\b[^>]*>', text, re.I):
        if not re.search(rf'\b{kind}=["\']{re.escape(key)}["\']', tag, re.I):
            continue
        m = re.search(r'\bcontent=["\']([^"\']*)["\']', tag, re.I)
        return m.group(1).strip() if m else None
    return None


def link_href(text, rel, hreflang=None):
    for m in re.finditer(r'<link\b[^>]*>', text, re.I):
        tag = m.group(0)
        rel_m = re.search(r'\brel=["\']([^"\']+)["\']', tag, re.I)
        href_m = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.I)
        if not rel_m or not href_m or rel not in rel_m.group(1).split():
            continue
        if hreflang is not None:
            lang_m = re.search(r'\bhreflang=["\']([^"\']+)["\']', tag, re.I)
            if not lang_m or lang_m.group(1) != hreflang:
                continue
        return href_m.group(1)
    return None


def public_url(rel):
    if rel == 'index.html':
        return BASE_URL
    if rel == 'en/index.html':
        return BASE_URL + 'en/'
    return BASE_URL + rel


def counterparts(rel):
    if rel.startswith('en/'):
        zh_rel = rel[3:]
        en_rel = rel
    else:
        zh_rel = rel
        en_rel = 'en/' + rel
    return public_url(zh_rel), public_url(en_rel)


for html in sorted(ROOT.rglob('*.html')):
    text = html.read_text(encoding='utf-8')
    rel = str(html.relative_to(ROOT))
    if rel == '404.html' or 'class="site-header"' not in text:
        continue
    checked.append(rel)

    title_match = re.search(r'<title>(.*?)</title>', text, re.I | re.S)
    title = title_match.group(1).strip() if title_match else None
    if not title:
        errors.append(f'{rel}: missing <title>')

    description = meta_content(text, 'name', 'description')
    if not description:
        errors.append(f'{rel}: missing meta description')

    expected_canonical = public_url(rel)
    canonical = link_href(text, 'canonical')
    if canonical != expected_canonical:
        errors.append(f'{rel}: canonical must be {expected_canonical}, got {canonical}')

    expected_locale = 'en_US' if rel.startswith('en/') else 'zh_CN'
    required_meta = {
        ('property', 'og:type'): 'website',
        ('property', 'og:title'): None,
        ('property', 'og:description'): None,
        ('property', 'og:url'): None,
        ('property', 'og:image'): SHARE_IMAGE,
        ('property', 'og:image:width'): '1200',
        ('property', 'og:image:height'): '630',
        ('property', 'og:image:alt'): None,
        ('property', 'og:locale'): expected_locale,
        ('name', 'twitter:card'): 'summary_large_image',
        ('name', 'twitter:title'): None,
        ('name', 'twitter:description'): None,
        ('name', 'twitter:image'): SHARE_IMAGE,
    }
    found_meta = {}
    for (kind, key), expected in required_meta.items():
        found = meta_content(text, kind, key)
        found_meta[key] = found
        if not found:
            errors.append(f'{rel}: missing {key}')
        elif expected is not None and found != expected:
            errors.append(f'{rel}: {key} should be {expected}, got {found}')

    if title:
        for key in ('og:title', 'twitter:title'):
            value = found_meta.get(key)
            if value and value != title:
                errors.append(f'{rel}: {key} must match <title> ({title}), got {value}')
    if description:
        for key in ('og:description', 'twitter:description'):
            value = found_meta.get(key)
            if value and value != description:
                errors.append(f'{rel}: {key} must match meta description')
    og_url = found_meta.get('og:url')
    if canonical and og_url and og_url != canonical:
        errors.append(f'{rel}: og:url must match canonical ({canonical}), got {og_url}')

    zh_url, en_url = counterparts(rel)
    expected_alternates = {
        'zh-CN': zh_url,
        'en': en_url,
        'x-default': zh_url,
    }
    for lang, expected in expected_alternates.items():
        actual = link_href(text, 'alternate', lang)
        if actual != expected:
            errors.append(f'{rel}: hreflang {lang} must be {expected}, got {actual}')

share_file = ROOT / 'assets/images/social/pai-share-v4.jpg'
if not share_file.is_file():
    errors.append('committed share image is missing: assets/images/social/pai-share-v4.jpg')

if errors:
    print('Share metadata validation failed:')
    for e in errors:
        print(' -', e)
    sys.exit(1)

print(f'Share metadata OK: {len(checked)} content pages; exact bilingual canonical/hreflang/locale metadata validated; image={SHARE_IMAGE}')
