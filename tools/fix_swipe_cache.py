from pathlib import Path

root = Path(__file__).resolve().parents[1]

site = root / 'assets/js/site.js'
text = site.read_text(encoding='utf-8')
replacements = {
    'const SWIPE_MIN_X=72;': 'const SWIPE_MIN_X=56;',
    'const SWIPE_MAX_MS=700;': 'const SWIPE_MAX_MS=1200;',
    'Math.abs(dx)<Math.abs(dy)*1.35': 'Math.abs(dx)<Math.abs(dy)*1.15',
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f'missing expected site.js token: {old}')
    text = text.replace(old, new, 1)
site.write_text(text, encoding='utf-8')

changed = 0
for html in root.rglob('*.html'):
    rel = html.relative_to(root)
    if any(part.startswith('.') for part in rel.parts):
        continue
    src = html.read_text(encoding='utf-8')
    dst = src.replace('site.js?v=20260919-11"', 'site.js?v=20260919-12"')
    dst = dst.replace('site.js?v=20260919-10"', 'site.js?v=20260919-12"')
    dst = dst.replace('site.js?v=20260919-9"', 'site.js?v=20260919-12"')
    dst = dst.replace('site.js"', 'site.js?v=20260919-12"')
    if dst != src:
        html.write_text(dst, encoding='utf-8')
        changed += 1

if changed == 0:
    raise SystemExit('no HTML site.js references updated')
print(f'updated site.js gesture thresholds and cache-busted {changed} HTML files')
