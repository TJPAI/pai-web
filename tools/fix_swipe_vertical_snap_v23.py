from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s=s.replace(old,new,1)

rep(
"""  const historyStateWithScroll=scrollY=>Object.assign({},history.state||{},{pai:true,scrollY});
""",
"""  const historyStateWithScroll=scrollY=>Object.assign({},history.state||{},{pai:true,scrollY});
  const scrollToInstant=y=>{
    const rootStyle=document.documentElement.style;
    const previous=rootStyle.scrollBehavior;
    rootStyle.scrollBehavior='auto';
    window.scrollTo(0,Math.max(0,Number(y)||0));
    requestAnimationFrame(()=>{ rootStyle.scrollBehavior=previous; });
  };
""",
'add instant scroll helper')

rep(
"""        scrollTo(0,restoredY);
""",
"""        scrollToInstant(restoredY);
""",
'restore position instantly')

rep(
"""        scrollTo(0,0);
""",
"""        scrollToInstant(0);
""",
'top instantly')

rep(
"""    const currentMain=document.querySelector('main');
    const mainDocumentTop=currentMain?Math.max(0,currentMain.getBoundingClientRect().top+window.scrollY):0;
    const targetPath=normalizedPath(url.pathname);
""",
"""    const currentMain=document.querySelector('main');
    const header=document.querySelector('.site-header');
    const mainDocumentTop=Math.max(0,header?.getBoundingClientRect().bottom||currentMain?.getBoundingClientRect().top||0);
    const targetPath=normalizedPath(url.pathname);
""",
'align preview to sticky header bottom')

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-22','site.js?v=20260919-23')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v22 references updated')
print(f'patched vertical snap and {changed} HTML files')
