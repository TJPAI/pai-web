from pathlib import Path

p=Path('assets/css/site.css')
s=p.read_text()
needle='''@media(max-width:768px){\n  .container{width:min(calc(100% - 36px),var(--max))}\n'''
repl='''@media(max-width:768px){\n  /* Keep the sticky mobile chrome on a stable Safari compositing layer.\n     Opaque paint avoids intermittent backdrop-filter disappearance during horizontal swipes. */\n  .site-header{background:#fff;backdrop-filter:none;-webkit-backdrop-filter:none;isolation:isolate;z-index:80}\n  .container{width:min(calc(100% - 36px),var(--max))}\n'''
if needle not in s:
    raise SystemExit('mobile media anchor not found')
s=s.replace(needle,repl,1)
p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        h=f.read_text()
        n=h.replace('site.css?v=20260919-11','site.css?v=20260919-12')
        if n!=h:
            f.write_text(n)
            changed+=1
if changed==0:
    raise SystemExit('no site.css cache refs updated')
print('updated',changed,'html files')
