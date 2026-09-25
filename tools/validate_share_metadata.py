#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://tjpai.github.io/pai-web/'
SHARE_IMAGE = BASE_URL + 'assets/icons/icon-512.png'
errors = []
checked = []


def meta_content(text, kind, key):
    for tag in re.findall(r'<meta\b[^>]*>', text, re.I):
        if not re.search(rf'\b{kind}=["\']{re.escape(key)}["\']', tag, re.I):
            continue
        m = re.search(r'\bcontent=["\']([^"\']*)["\']', tag, re.I)
        return m.group(1).strip() if m else None
    return None


def link_href(text, rel):
    for m in re.finditer(r'<link\b[^>]*>', text, re.I):
        tag = m.group(0)
        rel_m = re.search(r'\brel=["\']([^"\']+)["\']', tag, re.I)
        href_m = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.I)
        if rel_m and href_m and rel in rel_m.group(1).split():
            return href_m.group(1)
    return None


for html in sorted(ROOT.rglob('*.html')):
    text = html.read_text(encoding='utf-8')
    rel = str(html.relative_to(ROOT))
    # 404 is an error document, not a shareable content page.
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

    canonical = link_href(text, 'canonical')
    if not canonical or not canonical.startswith(BASE_URL):
        errors.append(f'{rel}: missing/invalid canonical')

    required_meta = {
        ('property', 'og:type'): 'website',
        ('property', 'og:title'): None,
        ('property', 'og:description'): None,
        ('property', 'og:url'): None,
        ('property', 'og:image'): SHARE_IMAGE,
        ('property', 'og:image:width'): '512',
        ('property', 'og:image:height'): '512',
        ('property', 'og:image:alt'): None,
        ('name', 'twitter:card'): 'summary',
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

    # Keep browser, Open Graph, and Twitter presentation aligned.
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

    for lang in ('zh-CN', 'en', 'x-default'):
        ok = False
        for tag in re.findall(r'<link\b[^>]*>', text, re.I):
            if (re.search(r'\brel=["\']alternate["\']', tag, re.I)
                    and re.search(rf'\bhreflang=["\']{re.escape(lang)}["\']', tag, re.I)
                    and re.search(r'\bhref=["\']https://tjpai\.github\.io/pai-web/', tag, re.I)):
                ok = True
                break
        if not ok:
            errors.append(f'{rel}: missing hreflang {lang}')

if errors:
    print('Share metadata validation failed:')
    for e in errors:
        print(' -', e)
    sys.exit(1)

print(f'Share metadata OK: {len(checked)} content pages; image={SHARE_IMAGE}')
