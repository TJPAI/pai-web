from pathlib import Path

SCRIPT = 'assets/js/menu-exclusive.js?v=20260925-01'

changed = 0
for path in Path('.').rglob('*.html'):
    if 'geosketch-mvp' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    if '</body>' not in text:
        continue

    depth = len(path.parent.parts)
    prefix = '../' * depth
    tag = f'<script src="{prefix}{SCRIPT}"></script>'

    # Source pages intentionally do not carry this deployment-only helper.
    # If the expected tag is already present, keep the transform idempotent.
    if tag in text:
        continue

    text = text.replace('</body>', tag + '</body>', 1)
    path.write_text(text, encoding='utf-8')
    changed += 1

print(f'Injected menu exclusivity helper into {changed} HTML files')
