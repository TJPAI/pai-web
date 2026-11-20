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
VISIBLE_DEFAULT = 2
for item in items:
    groups.setdefault(item['year'], []).append(item)

def esc(value):
    return escape(str(value), quote=True)

# Journal-title abbreviations follow standard IEEE bibliographic practice.
JOURNAL_ABBREVIATIONS = {
    'IEEE Communications Surveys & Tutorials': 'IEEE Commun. Surveys Tuts.',
    'IEEE Transactions on Vehicular Technology': 'IEEE Trans. Veh. Technol.',
    'IEEE Transactions on Network Science and Engineering': 'IEEE Trans. Netw. Sci. Eng.',
    'IEEE Communications Letters': 'IEEE Commun. Lett.',
    'IEEE Transactions on Cognitive Communications and Networking': 'IEEE Trans. Cogn. Commun. Netw.',
    'IEEE Transactions on Wireless Communications': 'IEEE Trans. Wireless Commun.',
    'IEEE Transactions on Information Forensics and Security': 'IEEE Trans. Inf. Forensics Security',
    'IEEE Transactions on Instrumentation and Measurement': 'IEEE Trans. Instrum. Meas.',
    'IEEE Transactions on Mobile Computing': 'IEEE Trans. Mobile Comput.',
    'IEEE Wireless Communications Letters': 'IEEE Wireless Commun. Lett.',
    'IEEE Transactions on Signal Processing': 'IEEE Trans. Signal Process.',
    'IEEE Transactions on Intelligent Transportation Systems': 'IEEE Trans. Intell. Transp. Syst.',
    'IEEE Transactions on Communications': 'IEEE Trans. Commun.',
    'IEEE Network': 'IEEE Netw.',
    'IEEE Internet of Things Journal': 'IEEE Internet Things J.',
    'IEEE Internet of Things Magazine': 'IEEE Internet Things Mag.',
    'IEEE Access': 'IEEE Access',
    'IEEE Sensors Journal': 'IEEE Sensors J.',
    'IET Blockchain': 'IET Blockchain',
    'IEEE Transactions on Industrial Informatics': 'IEEE Trans. Ind. Informat.',
    'IEEE Vehicular Technology Magazine': 'IEEE Veh. Technol. Mag.',
    'IEEE Journal on Selected Areas in Communications': 'IEEE J. Sel. Areas Commun.',
    'IEEE Wireless Communications': 'IEEE Wireless Commun.',
    'IEEE Journal on Selected Topics in Signal Processing': 'IEEE J. Sel. Topics Signal Process.',
    'IEEE Transactions on Human-Machine Systems': 'IEEE Trans. Human-Mach. Syst.',
}
CONFERENCE_ABBREVIATIONS = {
    '2025 IEEE/CIC International Conference on Communications in China (ICCC)': 'IEEE/CIC Int. Conf. Commun. China (ICCC)',
    '2025 IEEE/CIC International Conference on Communications in China (ICCC Workshops)': 'IEEE/CIC Int. Conf. Commun. China (ICCC Workshops)',
    '2025 IEEE Global Blockchain Conference (GBC)': 'IEEE Global Blockchain Conf. (GBC)',
    '2024 International Conference on Future Communications and Networks (FCN), Valletta, Malta': 'Int. Conf. Future Commun. Netw. (FCN), Valletta, Malta',
    '2023 IEEE Conference on Antenna Measurements and Applications (CAMA), Genoa, Italy': 'IEEE Conf. Antenna Meas. Appl. (CAMA), Genoa, Italy',
    '2022 IEEE 95th Vehicular Technology Conference (VTC2022-Spring)': 'IEEE 95th Veh. Technol. Conf. (VTC2022-Spring)',
    'ICC 2022 - IEEE International Conference on Communications': 'IEEE Int. Conf. Commun. (ICC)',
    '2026 IEEE International Conference on Communications Workshops (ICC Workshops)': 'IEEE Int. Conf. Commun. Workshops (ICC Workshops)',
}

def ieee_author(full_name):
    tokens = full_name.strip().split()
    assert len(tokens) >= 2, ('unrecognized author', full_name)
    initials = ''.join('-'.join(part[0].upper() + '.' for part in token.split('-')) + ' ' for token in tokens[:-1])
    return initials + tokens[-1]

def ieee_authors(names):
    authors = [ieee_author(name) for name in names.split(', ')]
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return authors[0] + ' and ' + authors[1]
    return ', '.join(authors[:-1]) + ', and ' + authors[-1]

def ieee_reference(pub):
    venue = pub['venue']
    # Remove machine-readable volume/pages fields without guessing absent fields.
    m = re.search(r', (?:vol\.|pp\.)', venue)
    base = venue[:m.start()] if m else venue
    details = venue[m.start()+2:] if m else ''
    if base in JOURNAL_ABBREVIATIONS:
        publication = '<em>' + esc(JOURNAL_ABBREVIATIONS[base]) + '</em>'
    else:
        assert base in CONFERENCE_ABBREVIATIONS, ('unknown venue', pub['doi'], base)
        publication = 'in <em>Proc. ' + esc(CONFERENCE_ABBREVIATIONS[base]) + '</em>'
    if pub.get('publication_status') == 'early_access':
        publication += ', early access'
    # Apply standard IEEE volume, issue, page-range and year punctuation.
    details = re.sub(r'(?<=\d)-(?=\d)', '–', details)
    author_title = esc(ieee_authors(pub['authors'])) + ', “' + esc(pub['title'].rstrip(' .')) + ',” '
    # IEEE journal citations put volume/pages before year; conference papers put year before pages.
    if base in CONFERENCE_ABBREVIATIONS:
        fields = [publication, str(pub['year'])]
        if details:
            fields.append(esc(details))
    else:
        fields = [publication + (', ' + esc(details) if details else ''), str(pub['year'])]
    fields.append('doi: ' + esc(pub['doi']))
    return author_title + ', '.join(fields) + '.'

for language, page in (('zh', 'publications.html'), ('en', 'en/publications.html')):
    en = language == 'en'
    parts = ['<div data-publications data-publications-static="1">', '<!-- publications:start -->']
    parts.append('<div class="publication-toolbar" data-pub-enhancement hidden><nav class="publication-years" aria-label="' + ('Publication years' if en else '论文年份') + '">')
    for year in groups:
        parts.append(f'<button type="button" class="publication-year-link" data-pub-year-jump="{year}">{year}</button>')
    if any(len(pubs) > VISIBLE_DEFAULT for pubs in groups.values()):
        parts.append('<button type="button" class="publication-year-link pub-toggle-all" data-pub-toggle-all="1" aria-expanded="false">' + ('Expand all' if en else '展开全部') + '</button>')
    parts.append('</nav></div>')
    for year, pubs in groups.items():
        count = f'{len(pubs)} publication' + ('s' if len(pubs) != 1 else '') if en else f'{len(pubs)} 篇论文'
        parts.append(f'<section class="pub-group" id="pub-year-{year}" data-year="{year}" data-expanded="false"><div class="pub-year-row"><h2 class="pub-year">{year}</h2><span>{count}</span></div>')
        for index, pub in enumerate(pubs):
            key = esc(pub.get('doi') or pub['title'])
            extra = index >= VISIBLE_DEFAULT
            class_name = 'pub is-collapsed' if extra else 'pub'
            parts.append(f'<article class="{class_name}" data-pub-extra="{int(extra)}" data-publication-key="{key}"><p class="pub-reference">{ieee_reference(pub)}</p>')
            if pub.get('doi'):
                doi = quote(pub['doi'].strip(), safe="/!~*'()")
                parts.append(f'<div class="pub-actions"><a href="https://doi.org/{esc(doi)}" target="_blank" rel="noopener noreferrer">DOI ↗</a></div>')
            parts.append('</article>')
        if len(pubs) > VISIBLE_DEFAULT:
            parts.append(f'<button type="button" class="pub-toggle" data-pub-toggle="{year}" data-pub-enhancement hidden aria-expanded="false">' + (f'View all {len(pubs)} ↓' if en else f'展开全部 {len(pubs)} 篇 ↓') + '</button>')
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
