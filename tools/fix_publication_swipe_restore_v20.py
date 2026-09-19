from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s=s.replace(old,new,1)

rep(
"""  const saveCurrentScroll=()=>{
    if(navigating) return;
    const y=rememberPageScroll(normalizedPath(),window.scrollY);
    try{ history.replaceState(historyStateWithScroll(y),'',location.href); }catch(_e){}
  };
""",
"""  const cacheCurrentPageSnapshot=()=>{
    try{ pageCache.set(location.href.split('#')[0],document.documentElement.outerHTML); }catch(_e){}
  };
  const saveCurrentScroll=()=>{
    if(navigating) return;
    const y=rememberPageScroll(normalizedPath(),window.scrollY);
    try{ history.replaceState(historyStateWithScroll(y),'',location.href); }catch(_e){}
  };
""",
'cache snapshot helper')

rep(
"""    saveCurrentScroll();
    const label=(link.textContent||'').trim();
""",
"""    saveCurrentScroll();
    cacheCurrentPageSnapshot();
    const label=(link.textContent||'').trim();
""",
'cache before click navigation')

rep(
"""      renderChrome();
      /* Dynamic page content must settle before restoring a remembered position.
         Publications can substantially change document height after JSON rendering. */
      await initPublications([]);
""",
"""      renderChrome();
      /* Preserve publication expansion state when a rendered snapshot is reused. */
      const preservedPublicationYears=[...next.querySelectorAll('.pub-group[data-expanded="true"]')]
        .map(section=>section.dataset.year).filter(Boolean);
      /* Dynamic page content must settle before restoring a remembered position.
         Publications can substantially change document height after JSON rendering. */
      await initPublications(preservedPublicationYears);
""",
'preserve dynamic publication state')

rep(
"""    const previewMaxScroll=Math.max(0,mainDocumentTop+previewMain.scrollHeight-innerHeight);
    const targetScroll=Math.min(rememberedScroll,previewMaxScroll);
    previewMain.style.top=`${mainDocumentTop-targetScroll}px`;
    swipePreview={shell,main:previewMain,url,direction,targetScroll};
""",
"""    const previewMaxScroll=Math.max(0,mainDocumentTop+previewMain.scrollHeight-innerHeight);
    const previewScroll=Math.min(rememberedScroll,previewMaxScroll);
    previewMain.style.top=`${mainDocumentTop-previewScroll}px`;
    /* Never let an unrendered/short preview clamp the real destination position. */
    swipePreview={shell,main:previewMain,url,direction,targetScroll:rememberedScroll,previewScroll};
""",
'do not clamp remembered destination by preview height')

rep(
"""    event.preventDefault();
    saveCurrentScroll();
    commitSwipe(direction).finally(()=>{ pageSwipeStart=null; });
""",
"""    event.preventDefault();
    saveCurrentScroll();
    cacheCurrentPageSnapshot();
    commitSwipe(direction).finally(()=>{ pageSwipeStart=null; });
""",
'cache before swipe commit')

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-19','site.js?v=20260919-20')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v19 site.js references updated')
print(f'patched publication swipe restoration and {changed} HTML files')
# trigger after workflow creation
