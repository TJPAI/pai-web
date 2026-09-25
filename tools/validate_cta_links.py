#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
write = '--write' in sys.argv[1:]

# Exact user-facing CTA contracts. Destination pages without a fragment must open at page top.
contracts = {
    'index.html': [
        ('研究方向 <span>→</span>', 'research.html'),
        ('联系我们 <span>→</span>', 'contact.html'),
        ('更多研究成果 →', 'publications.html'),
        ('了解更多平台信息 →', 'about.html#international-impact'),
        ('查看全部媒体报道 →', 'about.html#media-coverage'),
        ('加入 PAI →', 'join.html'),
    ],
    'en/index.html': [
        ('Research <span>→</span>', 'research.html'),
        ('Contact <span>→</span>', 'contact.html'),
        ('More research results →', 'publications.html'),
        ('More platform information →', 'about.html#international-impact'),
        ('View all media coverage →', 'about.html#media-coverage'),
        ('Join PAI →', 'join.html'),
    ],
    'join.html': [('联系我们 →', 'contact.html#recruitment')],
    'en/join.html': [('Contact us →', 'contact.html#recruitment')],
}

if write:
    fixes = {
        'index.html': [
            ('<a class="btn textual" href="join.html">加入我们 <span>→</span></a>',
             '<a class="btn textual" href="contact.html">联系我们 <span>→</span></a>'),
        ],
        'en/index.html': [
            ('<a class="btn textual" href="join.html">Join PAI <span>→</span></a>',
             '<a class="btn textual" href="contact.html">Contact <span>→</span></a>'),
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
    print(f'Canonicalized homepage CTA labels/links in {changed} page(s).')

errors = []
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
