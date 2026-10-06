#!/usr/bin/env python3
"""Reject temporary or retired repository artifacts before deployment."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
problems = []
for path in ROOT.iterdir():
    if path.name.startswith('__'):
        problems.append(f'temporary root artifact: {path.name}')
workflow_dir = ROOT / '.github' / 'workflows'
if workflow_dir.exists():
    for path in workflow_dir.glob('*-once.yml'):
        problems.append(f'one-off workflow left in repository: {path.relative_to(ROOT)}')
for rel in ('assets/js/home-logo.js', 'assets/css/home-logo.css'):
    if (ROOT / rel).exists():
        problems.append(f'retired homepage-logo asset still present: {rel}')
for html in ROOT.rglob('*.html'):
    if '_site' in html.parts:
        continue
    text = html.read_text(encoding='utf-8', errors='ignore')
    if 'home-logo.js' in text or 'home-logo.css' in text:
        problems.append(f'retired homepage-logo reference: {html.relative_to(ROOT)}')
if problems:
    raise SystemExit('Repository hygiene failed:\n- ' + '\n- '.join(problems))
print('Repository hygiene passed.')
