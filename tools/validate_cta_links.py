#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
write = '--write' in sys.argv[1:]

# Exact user-facing CTA contracts. Page-top destinations use #main-content so
# lightweight navigation never restores an old remembered scroll position.
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

# Repeated Explore links have the same visible label, so their destinations are
# validated directly rather than by label text.
required_fragment_hrefs = {
    'index.html': [
        'research.html#pnl',
        'research.html#iotng',
        'research.html#aibi',
    ],
    'en/index.html': [
        'research.html#pnl',
        'research.html#iotng',
        'research.html#aibi',
    ],
}

# These cross-page destinations are deliberately aligned exactly to the live
# header edge by anchor-navigation.js after direct or lightweight navigation.
precise_targets = {
    'research.html': {'pnl', 'iotng', 'aibi'},
    'en/research.html': {'pnl', 'iotng', 'aibi'},
    'about.html': {'international-impact', 'media-coverage'},
    'en/about.html': {'international-impact', 'media-coverage'},
    'contact.html': {'recruitment'},
    'en/contact.html': {'recruitment'},
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

# There is one native hash fallback. It aligns to the actual header edge rather
# than adding page-specific whitespace. JS then measures the live header for the
# exact final position after lightweight navigation.
anchor_css = (ROOT / 'assets/css/app-core.css').read_text(encoding='utf-8')
site_css = (ROOT / 'assets/css/site.css').read_text(encoding='utf-8')
if 'main [id]{scroll-margin-top:73px}' not in anchor_css:
    errors.append('assets/css/app-core.css: desktop hash fallback must align to the 72px header + 1px rule')
if '@media(max-width:768px){main [id]{scroll-margin-top:63px}}' not in anchor_css:
    errors.append('assets/css/app-core.css: mobile hash fallback must align to the 62px header + 1px rule')
if '.anchor-target{scroll-margin-top:' in site_css:
    errors.append('assets/css/site.css: duplicate anchor-target scroll-margin rule must not return')

anchor_js = (ROOT / 'assets/js/anchor-navigation.js').read_text(encoding='utf-8')
for token in ('alignHashTarget', "classList.contains('anchor-target')", 'MutationObserver'):
    if token not in anchor_js:
        errors.append(f'assets/js/anchor-navigation.js: missing cross-page anchor contract token {token!r}')

for rel, items in contracts.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    anchors = text.split('</a>')
    for label, href in items:
        expected = f'href="{href}"'
        if not any(expected in anchor and label in anchor for anchor in anchors):
            errors.append(f'{rel}: CTA "{label}" must link to {href}')

for rel, hrefs in required_fragment_hrefs.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for href in hrefs:
        if f'href="{href}"' not in text:
            errors.append(f'{rel}: required cross-page destination {href} is missing')

# Validate every deterministic contract fragment against a real destination ID.
contract_hrefs = []
for rel, items in contracts.items():
    contract_hrefs.extend((rel, href) for _label, href in items if '#' in href)
for rel, hrefs in required_fragment_hrefs.items():
    contract_hrefs.extend((rel, href) for href in hrefs)

for source_rel, href in contract_hrefs:
    parts = urlsplit(href)
    if not parts.fragment:
        continue
    destination = (ROOT / source_rel).parent / parts.path
    if parts.path == '':
        destination = ROOT / source_rel
    destination = destination.resolve()
    try:
        target_rel = destination.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f'{source_rel}: destination escapes site root: {href}')
        continue
    if not destination.exists():
        errors.append(f'{source_rel}: destination file does not exist: {href}')
        continue
    target_text = destination.read_text(encoding='utf-8')
    if not re.search(rf'\bid=["\']{re.escape(parts.fragment)}["\']', target_text):
        errors.append(f'{source_rel}: fragment #{parts.fragment} does not exist in {target_rel}')

# Precise landing targets must opt in explicitly; this is the JS contract used
# for live-header correction after lightweight <main> swaps.
for rel, target_ids in precise_targets.items():
    text = (ROOT / rel).read_text(encoding='utf-8')
    for target_id in target_ids:
        tag = re.search(rf'<[^>]+\bid=["\']{re.escape(target_id)}["\'][^>]*>', text)
        if not tag:
            errors.append(f'{rel}: missing precise target #{target_id}')
        elif not re.search(r'\bclass=["\'][^"\']*\banchor-target\b', tag.group(0)):
            errors.append(f'{rel}: #{target_id} must carry class anchor-target')

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
