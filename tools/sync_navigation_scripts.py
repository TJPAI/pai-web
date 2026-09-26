#!/usr/bin/env python3
"""Keep shared navigation assets identical for direct entry and in-site navigation."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STYLE = 'assets/css/home-logo.css?v=20260920-04'
SCRIPTS = ('assets/js/home-logo.js?v=20260926-01',
           'assets/js/anchor-navigation.js?v=20260925-03')
check_only = '--check' in sys.argv
errors = []
changed = 0
for path in ROOT.rglob('*.html'):
    if 'geosketch-mvp' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    if '</body>' not in text:
        continue
    relative = path.relative_to(ROOT)
    prefix = '../' * len(relative.parent.parts)
    style = f'<link rel="stylesheet" href="{prefix}{STYLE}">'
    scripts = [f'<script src="{prefix}{script}"></script>' for script in SCRIPTS]
    script_pattern = r'<script\b[^>]*src=["\'][^"\']*(?:menu-exclusive|anchor-navigation|home-logo)\.js[^"\']*["\'][^>]*></script>'
    style_pattern = r'<link\b[^>]*href=["\'][^"\']*home-logo\.css[^"\']*["\'][^>]*>'
    if re.findall(script_pattern, text) == scripts and re.findall(style_pattern, text) == [style]:
        continue
    if check_only:
        errors.append(str(relative))
        continue
    text = re.sub(script_pattern, '', text)
    text = re.sub(style_pattern, '', text)
    text = text.replace('</head>', style + '</head>', 1)
    text = text.replace('</body>', ''.join(scripts) + '</body>', 1)
    path.write_text(text, encoding='utf-8')
    changed += 1
if errors:
    sys.exit('Navigation assets out of sync: ' + ', '.join(errors))
print('Navigation assets passed.' if check_only else f'Updated {changed} page(s).')
