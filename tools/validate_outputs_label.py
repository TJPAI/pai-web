#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

site_js = (ROOT / 'assets/js/site.js').read_text(encoding='utf-8')
zh_outputs = (ROOT / 'publications.html').read_text(encoding='utf-8')
en_outputs = (ROOT / 'en/publications.html').read_text(encoding='utf-8')

# The public English label is Outputs while the stable URL remains publications.html.
if not re.search(r"\['Outputs','/en/publications\.html'\]", site_js):
    errors.append('assets/js/site.js: English navigation must label /en/publications.html as Outputs')

for required, description in (
    (r'<title>Outputs\s*\|\s*PAI Research Center</title>', 'document title'),
    (r'<h1\b[^>]*>Outputs</h1>', 'page H1'),
):
    if not re.search(required, en_outputs, re.I):
        errors.append(f'en/publications.html: {description} must remain Outputs')

for path in (ROOT / 'en').rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    rel = path.relative_to(ROOT)
    if '>Publications</a>' in text:
        errors.append(f'{rel}: stale Publications navigation label; use Outputs')

if 'outputs.html' in site_js or 'outputs.html' in en_outputs:
    errors.append('Outputs must keep the stable publications.html URL; outputs.html is not allowed')

# The visible publication range must be derived from the data, not manually drift.
items = []
for rel in ('data/publications.json', 'data/publications-archive.json'):
    try:
        data = json.loads((ROOT / rel).read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'{rel}: invalid JSON: {exc}')
        continue
    if not isinstance(data, list):
        errors.append(f'{rel}: expected a JSON array')
        continue
    items.extend(data)

if items:
    years = [item.get('year') for item in items if isinstance(item, dict)]
    if not years or any(not isinstance(year, int) for year in years):
        errors.append('publication data: every record must have an integer year')
    else:
        year_range = f'{min(years)}–{max(years)}'
        if f'<p>{year_range} · 按年份倒序</p>' not in zh_outputs:
            errors.append(f'publications.html: visible publication range must be {year_range}')
        if f'<p>{year_range} · reverse chronological</p>' not in en_outputs:
            errors.append(f'en/publications.html: visible publication range must be {year_range}')

if errors:
    print('Outputs label validation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

print(f'Outputs label validation passed; publication range={min(years)}–{max(years)}.' if items else 'Outputs label validation passed.')
