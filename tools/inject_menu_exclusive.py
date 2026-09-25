from pathlib import Path

SCRIPTS = (
    'assets/js/menu-exclusive.js?v=20260925-01',
    'assets/js/anchor-navigation.js?v=20260925-02',
)

changed = 0
for path in Path('.').rglob('*.html'):
    if 'geosketch-mvp' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    if '</body>' not in text:
        continue

    depth = len(path.parent.parts)
    prefix = '../' * depth
    tags = ''.join(f'<script src="{prefix}{script}"></script>' for script in SCRIPTS)

    expected = [f'<script src="{prefix}{script}"></script>' for script in SCRIPTS]
    if all(tag in text for tag in expected):
        continue

    for tag in expected:
        text = text.replace(tag, '')
    # Remove the previous anchor-navigation cache key if present in an already prepared artifact.
    text = text.replace(f'<script src="{prefix}assets/js/anchor-navigation.js?v=20260925-01"></script>', '')
    text = text.replace('</body>', tags + '</body>', 1)
    path.write_text(text, encoding='utf-8')
    changed += 1

print(f'Injected navigation helpers into {changed} HTML files')
