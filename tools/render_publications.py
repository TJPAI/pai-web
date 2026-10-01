#!/usr/bin/env python3
"""Render the canonical publication data into bilingual, crawlable source HTML."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
items = []
for name in ('publications.json', 'publications-archive.json'):
    items.extend(json.loads((ROOT / 'data' / name).read_text(encoding='utf-8')))
items.sort(key=lambda item: -item['year'])
groups = {}
for item in items:
    groups.setdefault(item['year'], []).append(item)

def esc(value):
    return escape(str(value), quote=True)

for language, page in (('zh', 'publications.html'), ('en', 'en/publications.html')):
    en = language == 'en'
    parts = ['<div data-publications data-publications-static="1">', '<!-- publications:start -->']
    parts.append('<div class="publication-toolbar" data-pub-enhancement hidden><nav class="publication-years" aria-label="' + ('Publication years' if en else '论文年份') + '">')
    for year in groups:
        parts.append(f'<button type="button" class="publication-year-link" data-pub-year-jump="{year}">{year}</button>')
    if any(len(pubs) > 3 for pubs in groups.values()):
        parts.append('<button type="button" class="publication-year-link pub-toggle-all" data-pub-toggle-all="1" aria-expanded="true">' + ('Collapse' if en else '收起') + '</button>')
    parts.append('</nav></div>')
    for year, pubs in groups.items():
        count = f'{len(pubs)} publication' + ('s' if len(pubs) != 1 else '') if en else f'{len(pubs)} 篇论文'
        parts.append(f'<section class="pub-group" id="pub-year-{year}" data-year="{year}" data-expanded="true"><div class="pub-year-row"><h2 class="pub-year">{year}</h2><span>{count}</span></div>')
        for index, pub in enumerate(pubs):
            key = esc(pub.get('doi') or pub['title'])
            parts.append(f'<article class="pub" data-pub-extra="{int(index >= 3)}" data-publication-key="{key}"><h3 class="title-item">{esc(pub["title"])}</h3><p class="pub-authors">{esc(pub["authors"])}</p><p class="pub-venue">{esc(pub["venue"])} · {year}</p>')
            if pub.get('doi'):
                doi = quote(pub['doi'].strip(), safe="/!~*'()")
                parts.append(f'<div class="pub-actions"><a href="https://doi.org/{esc(doi)}" target="_blank" rel="noopener noreferrer">DOI ↗</a></div>')
            parts.append('</article>')
        if len(pubs) > 3:
            parts.append(f'<button type="button" class="pub-toggle" data-pub-toggle="{year}" data-pub-enhancement hidden aria-expanded="true">' + ('Show less ↑' if en else '收起 ↑') + '</button>')
        parts.append('</section>')
    parts.append('<button type="button" class="pub-back-top" data-pub-back-top="1" data-pub-enhancement hidden>' + ('↑ Top' if en else '↑ 顶部') + '</button>')
    parts.append('<!-- publications:end --></div>')
    path = ROOT / page
    source = path.read_text(encoding='utf-8')
    pattern = r'<div data-publications(?: data-publications-static="1")?>\s*(?:<!-- publications:start -->.*?<!-- publications:end -->)?</div>'
    updated, count = re.subn(pattern, lambda _: '\n'.join(parts), source, flags=re.S)
    if count != 1:
        raise SystemExit(f'{page}: expected one publication container, got {count}')
    if '--check' in sys.argv:
        if source != updated:
            raise SystemExit(f'{page}: static publications are stale; run tools/render_publications.py')
    else:
        path.write_text(updated, encoding='utf-8')
    print(f'{page}: {len(items)} static publications verified' if '--check' in sys.argv else f'{page}: rendered {len(items)} publications')
