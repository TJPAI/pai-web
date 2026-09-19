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
    Object.assign(previewMain.style,{
""",
"""    const targetPath=normalizedPath(url.pathname);
    const targetScroll=rememberedPageScroll(targetPath);
    Object.assign(previewMain.style,{
""",
'preview remembered target')

rep(
"""    /* Swipe navigation always previews and lands at the destination page top.
       Browser history may still restore its own saved position separately. */
    previewMain.style.top=`${mainDocumentTop}px`;
    swipePreview={shell,main:previewMain,url,direction,targetScroll:0};
""",
"""    /* Use the same remembered page position as direct/menu navigation.
       A rendered snapshot is cached when leaving a page, so revisits can preview
       the real vertical position without clamping the final destination value. */
    const previewMaxScroll=Math.max(0,mainDocumentTop+previewMain.scrollHeight-innerHeight);
    const previewScroll=Math.min(targetScroll,previewMaxScroll);
    previewMain.style.top=`${mainDocumentTop-previewScroll}px`;
    swipePreview={shell,main:previewMain,url,direction,targetScroll,previewScroll};
""",
'preview remembered positioning')

rep(
"""    const targetUrl=preview.url;
    const targetScroll=0;
""",
"""    const targetUrl=preview.url;
    const targetScroll=rememberedPageScroll(normalizedPath(targetUrl.pathname));
""",
'commit remembered target')

rep(
"""    event.preventDefault();
    saveCurrentScroll();
    commitSwipe(direction).finally(()=>{ pageSwipeStart=null; });
""",
"""    event.preventDefault();
    saveCurrentScroll();
    /* Cache the fully rendered page before leaving it. This keeps dynamic pages
       such as Publications accurate when they later appear as a swipe preview. */
    cacheCurrentPageSnapshot();
    commitSwipe(direction).finally(()=>{ pageSwipeStart=null; });
""",
'cache rendered page before swipe')

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-24','site.js?v=20260919-25')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v24 site.js references updated')
print(f'restored swipe scroll memory and updated {changed} HTML files')
