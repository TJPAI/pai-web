from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s=s.replace(old,new,1)

rep(
"""  const applyPage=async(url,{historyMode='push',preserveScrollY=null,transitionDirection=0,gestureOffset=0}={})=>{
    if(navigating) return;
    navigating=true;
""",
"""  const applyPage=async(url,{historyMode='push',preserveScrollY=null,transitionDirection=0,gestureOffset=0}={})=>{
    if(navigating) return;
    if(scrollSaveTimer!==null){
      clearTimeout(scrollSaveTimer);
      scrollSaveTimer=null;
    }
    navigating=true;
""",
'cancel stale scroll timer')

rep(
"""      renderChrome();
      initPublications([]);
      setTimeout(()=>warmNavigation(),80);
      if(Number.isFinite(preserveScrollY)){
        await new Promise(resolve=>requestAnimationFrame(resolve));
""",
"""      renderChrome();
      /* Dynamic page content must settle before restoring a remembered position.
         Publications can substantially change document height after JSON rendering. */
      await initPublications([]);
      setTimeout(()=>warmNavigation(),80);
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
      if(Number.isFinite(preserveScrollY)){
""",
'wait for dynamic layout before restore')

rep(
"""      }else if(url.hash){
        document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView();
      }else{
        scrollTo(0,0);
      }
""",
"""      }else if(url.hash){
        document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView();
        const y=rememberPageScroll(normalizedPath(url.pathname),window.scrollY);
        try{ history.replaceState(historyStateWithScroll(y),'',location.href); }catch(_e){}
      }else{
        scrollTo(0,0);
        rememberPageScroll(normalizedPath(url.pathname),0);
        try{ history.replaceState(historyStateWithScroll(0),'',location.href); }catch(_e){}
      }
""",
'deterministic destination state')

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-18','site.js?v=20260919-19')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v18 site.js references updated')
print(f'patched site.js and {changed} HTML files')
