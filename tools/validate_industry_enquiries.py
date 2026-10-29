#!/usr/bin/env python3
"""Validate bilingual industry enquiry subjects against full project names."""
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import html
import re

ROOT = Path(__file__).resolve().parents[1]
FULL_ENGLISH = {
    'port': 'Drone-Based Port Vehicle Inventory System',
    'lidar': 'High-Precision LiDAR Localization System',
    'navigation': 'DWELT Integrated Positioning and Navigation System',
    'remote': 'Non-Invasive Vehicle Remote Driving Retrofit Kit',
    'earth': 'Compact Two-Way Through-the-Earth Wireless Communication System',
    'blasting': 'Through-the-Earth Wireless Remote Blasting Communication Technology',
    'gnn': 'AI Surrogate Model for Physical Simulation',
    'rom': 'Fast Real-Time Computing and Simulation Acceleration Model',
    'avatar': 'Real-Time Audio-Driven Digital Human Lip Synchronization',
    'did': 'Blockchain-Based Trusted Digital Identity System',
    'privacy': 'Privacy Computing and Trusted Data Collaboration Platform',
    'finance': 'Financial Blockchain Ecosystem Security and Risk Supervision Platform',
}
errors = []
for page, english in [('publications.html', False), ('en/publications.html', True)]:
    text = (ROOT / page).read_text(encoding='utf-8')
    cards = re.findall(r'<article class="industry-card" id="tech-([^"]+)">(.*?)</article>', text, re.S)
    if len(cards) != 12:
        errors.append(f'{page}: expected 12 technology cards, got {len(cards)}')
    for ident, card in cards:
        heading = re.search(r'<h3 class="title-item">([^<]+)</h3>', card)
        link = re.search(r'<a class="industry-link" href="([^"]+)">([^<]+)</a>', card)
        if not heading or not link:
            errors.append(f'{page}:{ident}: missing heading or enquiry link')
            continue
        expected = FULL_ENGLISH.get(ident) if english else html.unescape(heading.group(1))
        if not expected:
            errors.append(f'{page}:{ident}: unknown identity')
            continue
        url = html.unescape(link.group(1))
        subject = parse_qs(urlsplit(url).query).get('subject', [''])[0]
        if expected not in subject:
            errors.append(f'{page}:{ident}: full project name missing from email subject')
        if urlsplit(url).scheme != 'mailto':
            errors.append(f'{page}:{ident}: expected mailto')
        label = 'Enquiry →' if english else '咨询合作 →'
        if html.unescape(link.group(2)) != label:
            errors.append(f'{page}:{ident}: unexpected enquiry label')
if errors:
    raise SystemExit('\n'.join(errors))
print('Validated all 24 localized technology enquiry subjects.')
