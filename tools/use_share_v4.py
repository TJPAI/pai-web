from pathlib import Path

changed=0
for html in Path('.').rglob('*.html'):
    text=html.read_text(encoding='utf-8')
    new=text.replace('assets/images/social/pai-share-v3.jpg','assets/images/social/pai-share-v4.jpg')
    if new!=text:
        html.write_text(new,encoding='utf-8')
        changed+=1

# Keep validation guardrails aligned with the canonical share asset.
for rel in ('tools/validate.py','tools/validate_share_metadata.py'):
    p=Path(rel)
    text=p.read_text(encoding='utf-8')
    new=text.replace('pai-share-v3.jpg','pai-share-v4.jpg')
    if new!=text:
        p.write_text(new,encoding='utf-8')

print(f'updated {changed} html files and share-image validators')
if not changed:
    raise SystemExit('no share image references updated')
