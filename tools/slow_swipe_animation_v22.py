from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()

replacements={
    'const SWIPE_SETTLE_MS=300;':'const SWIPE_SETTLE_MS=330;',
    "animateElementTransform(current,currentFrom,'translate3d(0,0,0)',230)":"animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253)",
    "animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,230)":"animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)",
    "animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,300)":"animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330)",
    "animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',300)":"animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',330)",
}
for old,new in replacements.items():
    if old not in s:
        raise SystemExit(f'missing pattern: {old}')
    s=s.replace(old,new,1)
p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-21','site.js?v=20260919-22')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v21 references updated')
print(f'updated swipe timing and {changed} HTML files')
# trigger after workflow exists
