from pathlib import Path

TAG = '<script src="/pai-web/assets/js/menu-exclusive.js?v=20260925-01"></script>'

changed = 0
for path in Path('.').rglob('*.html'):
    if 'geosketch-mvp' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    if TAG in text:
        continue
    if '</body>' not in text:
        continue
    text = text.replace('</body>', TAG + '</body>', 1)
    path.write_text(text, encoding='utf-8')
    changed += 1

print(f'Injected menu exclusivity helper into {changed} HTML files')
