#!/usr/bin/env python3
"""Stage an explicit public-site tree for GitHub Pages upload.

Build tooling, repository configuration and maintenance documentation remain in the
repository but are not published under the website domain.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

# All root HTML files are public entry/error pages.
for source in ROOT.glob('*.html'):
    shutil.copy2(source, OUT / source.name)

PUBLIC_DIRS = (
    'assets',
    'data',
    'en',
    'people',
    'geosketch-mvp',
)
for rel in PUBLIC_DIRS:
    source = ROOT / rel
    if not source.is_dir():
        raise SystemExit(f'public artifact source directory missing: {rel}')
    shutil.copytree(source, OUT / rel)

PUBLIC_FILES = (
    'robots.txt',
    'sitemap.xml',
    'site.webmanifest',
    'sw.js',
)
for rel in PUBLIC_FILES:
    source = ROOT / rel
    if not source.is_file():
        raise SystemExit(f'public artifact source file missing: {rel}')
    shutil.copy2(source, OUT / rel)

cname = ROOT / 'CNAME'
if cname.is_file():
    shutil.copy2(cname, OUT / 'CNAME')

# GeoSketch remains directly accessible as a utility/demo, but it is not part of the
# institutional website's indexable content. Keep that boundary explicit in production.
geosketch = OUT / 'geosketch-mvp' / 'index.html'
geosketch_text = geosketch.read_text(encoding='utf-8')
robots_meta = '<meta name="robots" content="noindex,nofollow">'
if robots_meta not in geosketch_text:
    marker = '<title>GeoSketch MVP</title>'
    if geosketch_text.count(marker) != 1:
        raise SystemExit('geosketch-mvp/index.html: expected one GeoSketch title marker')
    geosketch.write_text(geosketch_text.replace(marker, marker + '\n' + robots_meta), encoding='utf-8')

# These files are build inputs only. The browser receives refine-bundle.css and the
# generated square share PNG for inner pages instead.
BUILD_ONLY_ASSETS = (
    'assets/css/refine.css',
    'assets/css/refine-base.css',
    'assets/css/app-core.css',
    'assets/css/typography.css',
)
for rel in BUILD_ONLY_ASSETS:
    target = OUT / rel
    if not target.is_file():
        raise SystemExit(f'expected build-only asset missing before public pruning: {rel}')
    target.unlink()

# Guard against accidentally publishing repository/build internals.
for forbidden in ('tools', 'config', 'templates', '.github', 'README.md', 'MAINTENANCE.md', 'PRODUCTION_CUTOVER.md'):
    if (OUT / forbidden).exists():
        raise SystemExit(f'public artifact unexpectedly contains {forbidden}')
for rel in BUILD_ONLY_ASSETS:
    if (OUT / rel).exists():
        raise SystemExit(f'public artifact unexpectedly contains build-only asset {rel}')

files = sum(1 for path in OUT.rglob('*') if path.is_file())
print(f'Prepared public Pages artifact at _site with {files} files.')
