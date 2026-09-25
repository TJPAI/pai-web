#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Keep in-page section targets visually aligned below the site header:
# desktop header 72px + 24px gap = 96px;
# mobile header 62px + 18px gap = 80px.
app_core = ROOT / 'assets/css/app-core.css'
text = app_core.read_text(encoding='utf-8')
old = 'main [id]{scroll-margin-top:88px}\n@media(max-width:768px){main [id]{scroll-margin-top:74px}}'
new = 'main [id]{scroll-margin-top:96px}\n@media(max-width:768px){main [id]{scroll-margin-top:80px}}'
if old not in text and new not in text:
    raise SystemExit('Unexpected app-core anchor spacing state')
if old in text:
    app_core.write_text(text.replace(old, new, 1), encoding='utf-8')

# Bust the imported component layer cache.
refine = ROOT / 'assets/css/refine.css'
text = refine.read_text(encoding='utf-8')
old_import = '@import url("./app-core.css?v=20260920-25");'
new_import = '@import url("./app-core.css?v=20260925-01");'
if old_import not in text and new_import not in text:
    raise SystemExit('Unexpected app-core import version')
if old_import in text:
    refine.write_text(text.replace(old_import, new_import, 1), encoding='utf-8')

# Bump the public refine.css cache key and keep the normalizer contract in sync.
normalizer = ROOT / 'tools/normalize_asset_versions.py'
text = normalizer.read_text(encoding='utf-8')
old_version = 'REFINE_VERSION = "20260925-04"'
new_version = 'REFINE_VERSION = "20260925-05"'
if old_version not in text and new_version not in text:
    raise SystemExit('Unexpected refine cache-key contract')
if old_version in text:
    normalizer.write_text(text.replace(old_version, new_version, 1), encoding='utf-8')

html_changed = 0
for path in ROOT.rglob('*.html'):
    if 'geosketch-mvp' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    updated = text.replace('refine.css?v=20260925-04', 'refine.css?v=20260925-05')
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        html_changed += 1

# Extend the CTA validator so the visual landing-offset contract cannot regress.
validator = ROOT / 'tools/validate_cta_links.py'
text = validator.read_text(encoding='utf-8')
marker = "errors = []\n"
guard = """errors = []\n\n# Fixed section targets share one visual landing rhythm below the sticky/fixed header.\nanchor_css = (ROOT / 'assets/css/app-core.css').read_text(encoding='utf-8')\nif 'main [id]{scroll-margin-top:96px}' not in anchor_css:\n    errors.append('assets/css/app-core.css: desktop anchor targets must keep a 24px gap below the 72px header')\nif '@media(max-width:768px){main [id]{scroll-margin-top:80px}}' not in anchor_css:\n    errors.append('assets/css/app-core.css: mobile anchor targets must keep an 18px gap below the 62px header')\n"""
if 'desktop anchor targets must keep a 24px gap' not in text:
    if marker not in text:
        raise SystemExit('CTA validator insertion point not found')
    validator.write_text(text.replace(marker, guard, 1), encoding='utf-8')

print(f'Canonicalized anchor spacing; updated refine cache key in {html_changed} HTML file(s).')
