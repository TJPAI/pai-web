from pathlib import Path

js_path=Path('assets/js/site.js')
text=js_path.read_text()

def replace_once(old,new,label):
    global text
    if old not in text:
        raise SystemExit(f'{label} not found')
    text=text.replace(old,new,1)

replace_once(
"""  const historyStateWithScroll=scrollY=>Object.assign({},history.state||{},{pai:true,scrollY});
  const saveCurrentScroll=()=>{
    if(navigating) return;
    try{ history.replaceState(historyStateWithScroll(window.scrollY),'',location.href); }catch(_e){}
  };
""",
"""  const historyStateWithScroll=scrollY=>Object.assign({},history.state||{},{pai:true,scrollY});
  const PAGE_SCROLL_KEY='pai-page-scroll-v1';
  let pageScrollPositions={};
  try{ pageScrollPositions=JSON.parse(sessionStorage.getItem(PAGE_SCROLL_KEY)||'{}')||{}; }catch(_e){}
  const rememberPageScroll=(path,y)=>{
    const value=Math.max(0,Math.round(Number(y)||0));
    pageScrollPositions[path]=value;
    try{ sessionStorage.setItem(PAGE_SCROLL_KEY,JSON.stringify(pageScrollPositions)); }catch(_e){}
    return value;
  };
  const rememberedPageScroll=path=>Math.max(0,Number(pageScrollPositions[path])||0);
  const saveCurrentScroll=()=>{
    if(navigating) return;
    const y=rememberPageScroll(normalizedPath(),window.scrollY);
    try{ history.replaceState(historyStateWithScroll(y),'',location.href); }catch(_e){}
  };
""",
'scroll memory helpers')

replace_once(
"""  const SWIPE_SETTLE_MS=220;
""",
"""  const SWIPE_SETTLE_MS=300;
""",
'settle duration')

replace_once(
"""    const currentMain=document.querySelector('main');
    const mainDocumentTop=currentMain?Math.max(0,currentMain.getBoundingClientRect().top+window.scrollY):0;
    Object.assign(previewMain.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:`calc(100vh - ${mainDocumentTop}px)`,
""",
"""    const currentMain=document.querySelector('main');
    const mainDocumentTop=currentMain?Math.max(0,currentMain.getBoundingClientRect().top+window.scrollY):0;
    const targetPath=normalizedPath(url.pathname);
    const targetScroll=rememberedPageScroll(targetPath);
    const previewTop=mainDocumentTop-targetScroll;
    Object.assign(previewMain.style,{
      position:'absolute',top:`${previewTop}px`,left:'0',width:'100%',minHeight:'100vh',
""",
'preview remembered vertical position')

replace_once(
"""    swipePreview={shell,main:previewMain,url,direction};
""",
"""    swipePreview={shell,main:previewMain,url,direction,targetScroll};
""",
'preview state scroll')

replace_once(
"""      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',165),
      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,165)
""",
"""      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',230),
      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,230)
""",
'rebound duration')

replace_once(
"""    const targetUrl=preview.url;
    await Promise.all([
      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,205),
      animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',205)
    ]);
    try{
      scrollTo(0,0);
      await applyPage(targetUrl,{transitionDirection:0,preserveScrollY:0});
""",
"""    const targetUrl=preview.url;
    const targetScroll=Math.max(0,Number(preview.targetScroll)||0);
    await Promise.all([
      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,300),
      animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',300)
    ]);
    try{
      await applyPage(targetUrl,{transitionDirection:0,preserveScrollY:targetScroll});
""",
'commit duration and restored position')

# Remember destination after successful navigation too, after clamping to the actual page height.
replace_once(
"""      if(Number.isFinite(preserveScrollY)){
        const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        scrollTo(0,Math.min(preserveScrollY,maxY));
""",
"""      if(Number.isFinite(preserveScrollY)){
        const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        const restoredY=Math.min(preserveScrollY,maxY);
        scrollTo(0,restoredY);
        rememberPageScroll(normalizedPath(url.pathname),restoredY);
""",
'applyPage remembered destination')

js_path.write_text(text)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for path in Path('.').glob(pattern):
        html=path.read_text()
        newer=html.replace('site.js?v=20260919-16','site.js?v=20260919-17')
        if newer!=html:
            path.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no HTML site.js v16 references updated')
print(f'updated swipe timing/scroll memory and {changed} HTML files')
