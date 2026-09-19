from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s=s.replace(old,new,1)

rep(
"""    const targetPath=normalizedPath(url.pathname);
    const rememberedScroll=rememberedPageScroll(targetPath);
""",
"""    const targetPath=normalizedPath(url.pathname);
""",
'preview target memory removal')

rep(
"""    const previewMaxScroll=Math.max(0,mainDocumentTop+previewMain.scrollHeight-innerHeight);
    const previewScroll=Math.min(rememberedScroll,previewMaxScroll);
    previewMain.style.top=`${mainDocumentTop-previewScroll}px`;
    /* Never let an unrendered/short preview clamp the real destination position. */
    swipePreview={shell,main:previewMain,url,direction,targetScroll:rememberedScroll,previewScroll};
""",
"""    /* Swipe navigation always previews and lands at the destination page top.
       Browser history may still restore its own saved position separately. */
    previewMain.style.top=`${mainDocumentTop}px`;
    swipePreview={shell,main:previewMain,url,direction,targetScroll:0};
""",
'preview always top')

rep(
"""    const targetUrl=preview.url;
    const targetScroll=Math.max(0,Number(preview.targetScroll)||0);
""",
"""    const targetUrl=preview.url;
    const targetScroll=0;
""",
'commit target top')

rep(
"""    saveCurrentScroll();
    cacheCurrentPageSnapshot();
    commitSwipe(direction).finally(()=>{ pageSwipeStart=null; });
""",
"""    saveCurrentScroll();
    commitSwipe(direction).finally(()=>{ pageSwipeStart=null; });
""",
'no snapshot dependency for swipe')

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-20','site.js?v=20260919-21')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v20 site.js references updated')
print(f'patched swipe-to-top behavior and {changed} HTML files')
# trigger after workflow exists
