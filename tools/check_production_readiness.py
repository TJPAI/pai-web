#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

robots=(ROOT/'robots.txt').read_text(encoding='utf-8') if (ROOT/'robots.txt').exists() else ''
if re.search(r'(?im)^\s*Disallow:\s*/\s*$', robots):
    errors.append('robots.txt still blocks the entire site (Preview configuration)')
if 'https://ai.tongji.edu.cn/sitemap.xml' not in robots:
    errors.append('robots.txt does not point to the production sitemap')

sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8') if (ROOT/'sitemap.xml').exists() else ''
if 'tjpai.github.io/pai-web' in sitemap:
    errors.append('sitemap.xml still contains the GitHub Preview domain')
if 'https://ai.tongji.edu.cn/' not in sitemap:
    errors.append('sitemap.xml does not contain the production domain')

for html in ROOT.rglob('*.html'):
    text=html.read_text(encoding='utf-8')
    rel=html.relative_to(ROOT)
    if 'https://ai.tongji.edu.cn/new_web/image/' in text:
        errors.append(f'{rel}: still depends on temporary-site faculty image URLs')
    if 'tjpai.github.io/pai-web' in text:
        errors.append(f'{rel}: contains a hard-coded Preview URL')

# Publication PDFs are intentionally not maintained in this repository.
for rel in ('data/publications.json','data/publications-archive.json'):
    text=(ROOT/rel).read_text(encoding='utf-8')
    if '"pdf"' in text:
        errors.append(f'{rel}: contains a forbidden publication PDF field')

# Production must keep the same Safari-safe homepage image contract as Preview.
for rel in ('index.html','en/index.html'):
    text=(ROOT/rel).read_text(encoding='utf-8')
    for match in re.findall(r'<img\b[^>]*assets/images/home/[^>]+>', text, re.I):
        if not re.search(r'\bloading=["\']eager["\']', match, re.I):
            errors.append(f'{rel}: production homepage image is not eager-loaded')
        if not re.search(r'\bdecoding=["\']sync["\']', match, re.I):
            errors.append(f'{rel}: production homepage image is not synchronously decoded')

if errors:
    print('Production readiness check FAILED:')
    for e in errors:
        print('ERROR:', e)
    sys.exit(1)

print('Production readiness check passed.')
