#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
write = '--write' in sys.argv[1:]

# Exact user-facing CTA contracts. Page-top destinations use #main-content so
# lightweight navigation cannot restore an old remembered scroll position.
contracts = {
    'index.html': [
        ('研究方向 <span>→</span>', 'research.html#main-content'),
        ('联系我们 <span>→</span>', 'contact.html#main-content'),
        ('更多研究成果 →', 'publications.html#main-content'),
        ('了解更多平台信息 →', 'about.html#international-impact'),
        ('查看全部媒体报道 →', 'about.html#media-coverage'),
        ('加入 PAI →', 'join.html#main-content'),
    ],
    'en/index.html': [
        ('Research <span>→</span>', 'research.html#main-content'),
        ('Contact <span>→</span>', 'contact.html#main-content'),
        ('More research results →', 'publications.html#main-content'),
        ('More platform information →', 'about.html#international-impact'),
        ('View all media coverage →', 'about.html#media-coverage'),
        ('Join PAI →', 'join.html#main-content'),
    ],
    'join.html': [('联系我们 →', 'contact.html#recruitment')],
    'en/join.html': [('Contact Us →', 'contact.html#recruitment')],
}

if write:
    fixes = {
        'index.html': [
            ('href="research.html">研究方向 <span>→</span>', 'href="research.html#main-content">研究方向 <span>→</span>'),
            ('href="contact.html">联系我们 <span>→</span>', 'href="contact.html#main-content">联系我们 <span>→</span>'),
            ('href="publications.html">更多研究成果 →', 'href="publications.html#main-content">更多研究成果 →'),
            ('href="join.html">加入 PAI →', 'href="join.html#main-content">加入 PAI →'),
        ],
        'en/index.html': [
            ('href="research.html">Research <span>→</span>', 'href="research.html#main-content">Research <span>→</span>'),
            ('href="contact.html">Contact <span>→</span>', 'href="contact.html#main-content">Contact <span>→</span>'),
            ('href="publications.html">More research results →', 'href="publications.html#main-content">More research results →'),
            ('href="join.html">Join PAI →', 'href="join.html#main-content">Join PAI →'),
        ],
    }
    changed = 0
    for rel, replacements in fixes.items():
        path = ROOT / rel
        text = path.read_text(encoding='utf-8')
        updated = text
        for old, new in replacements:
            updated = updated.replace(old, new, 1)
        if updated != text:
            path.write_text(updated, encoding='utf-8')
            changed += 1
    print(f'Canonicalized deterministic CTA destinations in {changed} page(s).')

errors = []

# Fixed section targets share one visual landing rhythm below the sticky/fixed header.
anchor_css = (ROOT / 'assets/css/app-core.css').read_text(encoding='utf-8')
if 'main [id]{scroll-margin-top:96px}' not in anchor_css:
    errors.append('assets/css/app-core.css: desktop anchor targets must keep a 24px gap below the 72px header')
if '@media(max-width:768px){main [id]{scroll-margin-top:80px}}' not in anchor_css:
    errors.append('assets/css/app-core.css: mobile anchor targets must keep an 18px gap below the 62px header')
for rel, items in contracts.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for label, href in items:
        expected = f'href="{href}"'
        # Require the intended label and destination to occur in the same anchor.
        if not any(expected in anchor and label in anchor for anchor in text.split('</a>')):
            errors.append(f'{rel}: CTA "{label}" must link to {href}')

# Explicitly reject the old Chinese hero CTA so it cannot silently return.
zh_home = (ROOT / 'index.html').read_text(encoding='utf-8')
if '<a class="btn textual" href="join.html">加入我们 <span>→</span></a>' in zh_home:
    errors.append('index.html: old hero CTA “加入我们” must be replaced by “联系我们”')

if errors:
    print('CTA link validation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

print('CTA link validation passed.')
