#!/usr/bin/env python3
"""Build a deployment-only CSS bundle from the layered refine entry point.

Source remains split for maintainability. The deployed artifact replaces links to
refine.css with refine-bundle.css so browsers do not pay an @import waterfall.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / 'assets' / 'css'
ENTRY = CSS / 'refine.css'
OUT = CSS / 'refine-bundle.css'

entry = ENTRY.read_text(encoding='utf-8')
imports = re.findall(r'^@import\s+url\(["\'](\./[^?"\']+)(?:\?[^"\']*)?["\']\);\s*$', entry, re.M)
if not imports:
    raise SystemExit('refine.css has no local @import layers to bundle')

parts = [
    '/* Generated deployment bundle. Source of truth remains refine.css and its imported layers. */\n'
]
for rel in imports:
    path = (CSS / rel.removeprefix('./')).resolve()
    if path.parent != CSS.resolve() or not path.is_file():
        raise SystemExit(f'Unsupported refine import: {rel}')
    parts.append(f'\n/* ---- {path.name} ---- */\n')
    parts.append(path.read_text(encoding='utf-8').rstrip() + '\n')

entry_without_imports = re.sub(r'^@import\s+url\(["\']\./[^"\']+["\']\);\s*\n?', '', entry, flags=re.M)
parts.append('\n/* ---- refine.css page-level refinements ---- */\n')
parts.append(entry_without_imports.lstrip())
OUT.write_text(''.join(parts), encoding='utf-8')

changed = 0
pattern = re.compile(r'(?P<prefix>(?:\.\./)*)assets/css/refine\.css(?P<query>\?v=[^"\']+)?')
for html in ROOT.rglob('*.html'):
    rel = html.relative_to(ROOT)
    if 'templates' in rel.parts or 'geosketch-mvp' in rel.parts:
        continue
    text = html.read_text(encoding='utf-8')
    updated = pattern.sub(lambda m: f"{m.group('prefix')}assets/css/refine-bundle.css{m.group('query') or ''}", text)
    if updated != text:
        html.write_text(updated, encoding='utf-8')
        changed += 1

print(f'Built {OUT.relative_to(ROOT)} from {len(imports)} layers and rewrote {changed} HTML page(s) for deployment.')
