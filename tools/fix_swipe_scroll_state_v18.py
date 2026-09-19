from pathlib import Path

js_path=Path('assets/js/site.js')
text=js_path.read_text()

def replace_once(old,new,label):
    global text
    if old not in text:
        raise SystemExit(f'{label} not found')
    text=text.replace(old,new,1)

replace_once(
"""  const normalizedPath=()=>{
    let path=location.pathname;
""",
"""  const normalizedPath=(pathname=location.pathname)=>{
    let path=pathname||'/';
""",
'normalizedPath argument')

replace_once(
"""    const currentMain=document.querySelector('main');
    const mainDocumentTop=currentMain?Math.max(0,currentMain.getBoundingClientRect().top+window.scrollY):0;
    const targetPath=normalizedPath(url.pathname);
    const targetScroll=rememberedPageScroll(targetPath);
    const previewTop=mainDocumentTop-targetScroll;
    Object.assign(previewMain.style,{
      position:'absolute',top:`${previewTop}px`,left:'0',width:'100%',minHeight:'100vh',
""",
"""    const currentMain=document.querySelector('main');
    const mainDocumentTop=currentMain?Math.max(0,currentMain.getBoundingClientRect().top+window.scrollY):0;
    const targetPath=normalizedPath(url.pathname);
    const rememberedScroll=rememberedPageScroll(targetPath);
    Object.assign(previewMain.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',
""",
'preview initial top')

replace_once(
"""    shell.appendChild(previewMain);
    document.body.appendChild(shell);
    swipePreview={shell,main:previewMain,url,direction,targetScroll};
""",
"""    shell.appendChild(previewMain);
    document.body.appendChild(shell);
    const previewMaxScroll=Math.max(0,mainDocumentTop+previewMain.scrollHeight-innerHeight);
    const targetScroll=Math.min(rememberedScroll,previewMaxScroll);
    previewMain.style.top=`${mainDocumentTop-targetScroll}px`;
    swipePreview={shell,main:previewMain,url,direction,targetScroll};
""",
'preview clamp')

replace_once(
"""      if(Number.isFinite(preserveScrollY)){
        const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        const restoredY=Math.min(preserveScrollY,maxY);
        scrollTo(0,restoredY);
        rememberPageScroll(normalizedPath(url.pathname),restoredY);
""",
"""      if(Number.isFinite(preserveScrollY)){
        await new Promise(resolve=>requestAnimationFrame(resolve));
        const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        const restoredY=Math.min(Math.max(0,preserveScrollY),maxY);
        scrollTo(0,restoredY);
        rememberPageScroll(normalizedPath(url.pathname),restoredY);
        try{ history.replaceState(historyStateWithScroll(restoredY),'',location.href); }catch(_e){}
""",
'authoritative restore')

js_path.write_text(text)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for path in Path('.').glob(pattern):
        html=path.read_text()
        newer=html.replace('site.js?v=20260919-17','site.js?v=20260919-18')
        if newer!=html:
            path.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no HTML site.js v17 references updated')
print(f'fixed swipe scroll state and updated {changed} HTML files')
# trigger
