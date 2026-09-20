from pathlib import Path

changed=0
for html in Path('.').rglob('*.html'):
    text=html.read_text(encoding='utf-8')
    new=text.replace('assets/images/social/pai-share-v3.jpg','assets/images/social/pai-share-v4.jpg')
    if new!=text:
        html.write_text(new,encoding='utf-8')
        changed+=1
print(f'updated {changed} html files')
if not changed:
    raise SystemExit('no share image references updated')
