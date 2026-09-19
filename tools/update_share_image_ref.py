from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = 'https://tjpai.github.io/pai-web/assets/images/social/pai-share.png'
NEW = 'https://tjpai.github.io/pai-web/assets/images/social/pai-share-v2.png'
changed = []
for p in ROOT.rglob('*.html'):
    text = p.read_text(encoding='utf-8')
    if OLD in text:
        p.write_text(text.replace(OLD, NEW), encoding='utf-8')
        changed.append(str(p.relative_to(ROOT)))
print('updated', len(changed), 'html files')
