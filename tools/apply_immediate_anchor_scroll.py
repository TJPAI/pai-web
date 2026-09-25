#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

site = ROOT / 'assets/js/site.js'
text = site.read_text(encoding='utf-8')
old = """      const hasRequestedScroll=Number.isFinite(preserveScrollY);\n      if(hasRequestedScroll){\n        const provisionalMaxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);\n        scrollToInstant(Math.min(Math.max(0,preserveScrollY),provisionalMaxY));\n      }else if(!url.hash){\n        scrollToInstant(0);\n      }\n\n      const preservedPublicationYears=[...next.querySelectorAll('.pub-group[data-expanded=\"true\"]')]\n"""
new = """      const hasRequestedScroll=Number.isFinite(preserveScrollY);\n      if(hasRequestedScroll){\n        const provisionalMaxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);\n        scrollToInstant(Math.min(Math.max(0,preserveScrollY),provisionalMaxY));\n      }else if(url.hash){\n        const target=document.getElementById(decodeURIComponent(url.hash.slice(1)));\n        if(target) target.scrollIntoView();\n        else scrollToInstant(0);\n      }else{\n        scrollToInstant(0);\n      }\n\n      const preservedPublicationYears=[...next.querySelectorAll('.pub-group[data-expanded=\"true\"]')]\n"""
if old not in text and new not in text:
    raise SystemExit('Unexpected site.js anchor-scroll state')
if old in text:
    site.write_text(text.replace(old, new, 1), encoding='utf-8')

normalizer = ROOT / 'tools/normalize_asset_versions.py'
text = normalizer.read_text(encoding='utf-8')
old_v = 'SITE_JS_VERSION = "20260925-03"'
new_v = 'SITE_JS_VERSION = "20260925-04"'
if old_v not in text and new_v not in text:
    raise SystemExit('Unexpected site.js cache-key contract')
if old_v in text:
    normalizer.write_text(text.replace(old_v, new_v, 1), encoding='utf-8')

changed = 0
for path in ROOT.rglob('*.html'):
    if 'geosketch-mvp' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    updated = text.replace('site.js?v=20260925-03', 'site.js?v=20260925-04')
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

print(f'Applied immediate anchor positioning before async page initialization; updated site.js cache key in {changed} HTML file(s).')
