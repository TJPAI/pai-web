from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()
old="""    const label=(link.textContent||'').trim();
    const isLanguageSwitch=label==='EN'||label==='中文';
    const options=isLanguageSwitch?{preserveScrollY:window.scrollY}:undefined;
    applyPage(url,options).catch(()=>{ location.href=url.href; });
"""
new="""    const label=(link.textContent||'').trim();
    const isLanguageSwitch=label==='EN'||label==='中文';
    let options;
    if(isLanguageSwitch){
      options={preserveScrollY:window.scrollY};
    }else if(!url.hash){
      /* Direct link/menu navigation restores the target page's last position.
         Swipe navigation remains intentionally top-aligned via preserveScrollY: 0. */
      options={preserveScrollY:rememberedPageScroll(normalizedPath(url.pathname))};
    }
    applyPage(url,options).catch(()=>{ location.href=url.href; });
"""
if old not in s:
    raise SystemExit('click navigation block not found')
s=s.replace(old,new,1)
p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-23','site.js?v=20260919-24')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v23 references updated')
print(f'restored click scroll memory and updated {changed} HTML files')
