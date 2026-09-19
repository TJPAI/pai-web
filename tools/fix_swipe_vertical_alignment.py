from pathlib import Path

js=Path('assets/js/site.js')
text=js.read_text()

old="""    Object.assign(previewMain.style,{
      position:'absolute',top:'0',left:'0',width:'100%',minHeight:'100vh',
      margin:'0',willChange:'transform',pointerEvents:'none',
      background:getComputedStyle(document.body).backgroundColor||'#fff',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
"""
new="""    const currentMain=document.querySelector('main');
    const mainDocumentTop=currentMain?Math.max(0,currentMain.getBoundingClientRect().top+window.scrollY):0;
    Object.assign(previewMain.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:`calc(100vh - ${mainDocumentTop}px)`,
      margin:'0',willChange:'transform',pointerEvents:'none',
      background:getComputedStyle(document.body).backgroundColor||'#fff',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
"""
if old not in text:
    raise SystemExit('preview positioning block not found')
text=text.replace(old,new,1)

# Keep the destination page at its final top position before preview removal, avoiding a second vertical settle.
old2="""    try{
      await applyPage(targetUrl,{transitionDirection:0});
    }finally{
      destroySwipePreview();
      setTimeout(warmSwipeNeighbors,60);
    }
"""
new2="""    try{
      scrollTo(0,0);
      await applyPage(targetUrl,{transitionDirection:0,preserveScrollY:0});
    }finally{
      destroySwipePreview();
      setTimeout(warmSwipeNeighbors,60);
    }
"""
if old2 not in text:
    raise SystemExit('commit swipe block not found')
text=text.replace(old2,new2,1)

js.write_text(text)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for path in Path('.').glob(pattern):
        html=path.read_text()
        newer=html.replace('site.js?v=20260919-15','site.js?v=20260919-16')
        if newer!=html:
            path.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no site.js v15 references found')
print(f'fixed preview vertical alignment and updated {changed} HTML files')
