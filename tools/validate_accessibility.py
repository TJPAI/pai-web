#!/usr/bin/env python3
"""Static accessibility contract checks for deployable HTML pages."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', 'node_modules', 'templates', 'tmp', 'geosketch-mvp'}
errors = []

site_js = (ROOT / 'assets/js/site.js').read_text(encoding='utf-8')
runtime_creates_mobile_nav = (
    "document.createElement('nav')" in site_js
    and "mobile.className='mobile-menu'" in site_js
    and "mobile.setAttribute('aria-label'" in site_js
)

pages = []
for path in ROOT.rglob('*.html'):
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED for part in rel.parts):
        continue
    pages.append(path)

for path in sorted(pages):
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding='utf-8')
    custom_404 = rel == '404.html'

    lang_match = re.search(r'<html\b[^>]*\blang=["\']([^"\']+)["\']', text, re.I)
    expected_lang = 'en' if rel.startswith('en/') else 'zh-CN'
    if not lang_match:
        errors.append(f'{rel}: missing html lang attribute')
    elif lang_match.group(1).lower() != expected_lang.lower():
        errors.append(f'{rel}: html lang={lang_match.group(1)!r}; expected {expected_lang!r}')

    h1_count = len(re.findall(r'<h1\b', text, re.I))
    if h1_count != 1:
        errors.append(f'{rel}: expected exactly one h1; found {h1_count}')

    main_match = re.search(r'<main\b[^>]*>(.*?)</main>', text, re.I | re.S)
    if main_match:
        heading_levels = [int(level) for level in re.findall(r'<h([1-6])\b', main_match.group(1), re.I)]
        if heading_levels and heading_levels[0] != 1:
            errors.append(f'{rel}: first heading inside main must be h1, found h{heading_levels[0]}')
        for previous, current in zip(heading_levels, heading_levels[1:]):
            if current > previous + 1:
                errors.append(f'{rel}: heading level jumps from h{previous} to h{current}')
    else:
        errors.append(f'{rel}: missing main landmark')

    # The standalone 404 page intentionally uses a minimal shell with a single main
    # landmark and no repeated site navigation. Main-site pages must expose the shared
    # skip target explicitly.
    if custom_404:
        if len(re.findall(r'<main\b', text, re.I)) != 1:
            errors.append(f'{rel}: expected exactly one main landmark')
    else:
        main_ids = re.findall(r'<main\b[^>]*\bid=["\']main-content["\']', text, re.I)
        if len(main_ids) != 1:
            errors.append(f'{rel}: expected exactly one <main id="main-content">')
        if not re.search(r'<a\b[^>]*class=["\'][^"\']*\bskip-link\b[^"\']*["\'][^>]*href=["\']#main-content["\']', text, re.I):
            errors.append(f'{rel}: missing skip link to #main-content')

    for tag in re.findall(r'<img\b[^>]*>', text, re.I):
        if not re.search(r'\balt=["\'][^"\']*["\']', tag, re.I):
            errors.append(f'{rel}: image missing alt attribute: {tag[:120]}')

    for tag in re.findall(r'<a\b[^>]*\btarget=["\']_blank["\'][^>]*>', text, re.I):
        rel_attr = re.search(r'\brel=["\']([^"\']*)["\']', tag, re.I)
        if not rel_attr or 'noopener' not in rel_attr.group(1).lower().split():
            errors.append(f'{rel}: target="_blank" link missing rel="noopener": {tag[:140]}')

    for value in re.findall(r'\btabindex=["\']([^"\']+)["\']', text, re.I):
        try:
            if int(value) > 0:
                errors.append(f'{rel}: positive tabindex={value} disrupts document focus order')
        except ValueError:
            errors.append(f'{rel}: non-integer tabindex={value!r}')

    if 'class="site-header"' in text:
        menu = re.search(r'<button\b[^>]*class=["\'][^"\']*\bmenu-btn\b[^"\']*["\'][^>]*>', text, re.I)
        if not menu:
            errors.append(f'{rel}: missing mobile menu button')
        else:
            tag = menu.group(0)
            for attr in ('aria-label', 'aria-expanded', 'aria-controls'):
                if not re.search(rf'\b{attr}=["\'][^"\']+["\']', tag, re.I):
                    errors.append(f'{rel}: mobile menu button missing {attr}')

        if not re.search(r'<nav\b[^>]*class=["\'][^"\']*\bnav-links\b[^"\']*["\'][^>]*\baria-label=["\'][^"\']+["\']', text, re.I):
            errors.append(f'{rel}: desktop navigation missing aria-label')

        has_mobile_nav = bool(re.search(
            r'<nav\b[^>]*class=["\'][^"\']*\bmobile-menu\b[^"\']*["\'][^>]*\baria-label=["\'][^"\']+["\']',
            text, re.I
        ))
        if not has_mobile_nav and not runtime_creates_mobile_nav:
            errors.append(f'{rel}: mobile navigation missing aria-label and runtime fallback')

    for tag in re.findall(r'<iframe\b[^>]*>', text, re.I):
        if not re.search(r'\btitle=["\'][^"\']+["\']', tag, re.I):
            errors.append(f'{rel}: iframe missing title attribute')

if errors:
    print('Accessibility contract validation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

print(f'Accessibility contract validation passed on {len(pages)} HTML page(s), including semantic heading order.')
