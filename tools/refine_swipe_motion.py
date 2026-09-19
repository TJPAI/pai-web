from pathlib import Path

js_path = Path('assets/js/site.js')
text = js_path.read_text()

old_sig = "const applyPage=async(url,{historyMode='push',preserveScrollY=null}={})=>{"
new_sig = "const applyPage=async(url,{historyMode='push',preserveScrollY=null,transitionDirection=0}={})=>{"
if old_sig not in text:
    raise SystemExit('applyPage signature not found')
text = text.replace(old_sig, new_sig, 1)

old_replace = """      /* Move the URL before attaching fetched markup so relative assets resolve\n         against the destination page immediately (important on iPhone Safari). */
      const destinationScroll=Number.isFinite(preserveScrollY)?preserveScrollY:0;
      if(historyMode==='push') history.pushState({pai:true,scrollY:destinationScroll},'',url.href);
      else if(historyMode==='replace') history.replaceState({pai:true,scrollY:destinationScroll},'',url.href);

      currentMain.replaceWith(document.importNode(nextMain,true));
      document.title=next.title||document.title;
"""
new_replace = """      const reduceMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
      const animateMain=async(node,keyframes,options)=>{
        if(!node||reduceMotion||!transitionDirection||typeof node.animate!=='function') return;
        try{
          const animation=node.animate(keyframes,options);
          await animation.finished;
        }catch(_e){}
      };
      const shift=transitionDirection>0?-18:18;
      await animateMain(currentMain,[
        {transform:'translate3d(0,0,0)',opacity:1},
        {transform:`translate3d(${shift}px,0,0)`,opacity:.72}
      ],{duration:115,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});

      /* Move the URL before attaching fetched markup so relative assets resolve\n         against the destination page immediately (important on iPhone Safari). */
      const destinationScroll=Number.isFinite(preserveScrollY)?preserveScrollY:0;
      if(historyMode==='push') history.pushState({pai:true,scrollY:destinationScroll},'',url.href);
      else if(historyMode==='replace') history.replaceState({pai:true,scrollY:destinationScroll},'',url.href);

      const incomingMain=document.importNode(nextMain,true);
      currentMain.replaceWith(incomingMain);
      document.title=next.title||document.title;
"""
if old_replace not in text:
    raise SystemExit('applyPage replacement block not found')
text = text.replace(old_replace, new_replace, 1)

old_scroll = """      if(Number.isFinite(preserveScrollY)){
        requestAnimationFrame(()=>{
          const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
          scrollTo(0,Math.min(preserveScrollY,maxY));
        });
      }else if(url.hash){
        requestAnimationFrame(()=>document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView());
      }else{
        scrollTo(0,0);
      }
"""
new_scroll = """      if(Number.isFinite(preserveScrollY)){
        const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        scrollTo(0,Math.min(preserveScrollY,maxY));
      }else if(url.hash){
        document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView();
      }else{
        scrollTo(0,0);
      }

      if(transitionDirection&&!reduceMotion){
        const incomingShift=transitionDirection>0?18:-18;
        await new Promise(resolve=>requestAnimationFrame(resolve));
        await animateMain(incomingMain,[
          {transform:`translate3d(${incomingShift}px,0,0)`,opacity:.72},
          {transform:'translate3d(0,0,0)',opacity:1}
        ],{duration:190,easing:'cubic-bezier(.2,.72,.22,1)',fill:'both'});
      }
"""
if old_scroll not in text:
    raise SystemExit('scroll block not found')
text = text.replace(old_scroll, new_scroll, 1)

old_touchstart_tail = """    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang};
  },{passive:true});

  document.addEventListener('touchend',event=>{
"""
new_touchstart_tail = """    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang,locked:false,warmedDirection:0};
  },{passive:true});

  /* Once horizontal intent is clear, own that gesture so Safari cannot add vertical drift. */
  document.addEventListener('touchmove',event=>{
    const start=pageSwipeStart;
    if(!start||event.touches.length!==1) return;
    const touch=event.touches[0];
    const dx=touch.clientX-start.x;
    const dy=touch.clientY-start.y;
    const ax=Math.abs(dx);
    const ay=Math.abs(dy);

    if(!start.locked){
      if(ax<8&&ay<8) return;
      if(ay>ax*1.08){ pageSwipeStart=null; return; }
      if(ax>=8&&ax>ay*1.18) start.locked=true;
    }
    if(!start.locked) return;

    event.preventDefault();
    const direction=dx<0?1:-1;
    if(direction!==start.warmedDirection){
      start.warmedDirection=direction;
      const pages=swipePageOrder[start.lang];
      const index=pages.indexOf(start.path);
      if(index>=0){
        const targetPath=pages[(index+direction+pages.length)%pages.length];
        fetchPage(new URL(root(targetPath),location.origin)).catch(()=>{});
      }
    }
  },{passive:false});

  document.addEventListener('touchcancel',()=>{ pageSwipeStart=null; },{passive:true});

  document.addEventListener('touchend',event=>{
"""
if old_touchstart_tail not in text:
    raise SystemExit('touchstart tail not found')
text = text.replace(old_touchstart_tail, new_touchstart_tail, 1)

old_end_check = """    if(!start||event.changedTouches.length!==1||navigating) return;
    const touch=event.changedTouches[0];
    const dx=touch.clientX-start.x;
    const dy=touch.clientY-start.y;
    const elapsed=performance.now()-start.time;
    if(elapsed>SWIPE_MAX_MS||Math.abs(dx)<SWIPE_MIN_X||Math.abs(dx)<Math.abs(dy)*1.15) return;
"""
new_end_check = """    if(!start||!start.locked||event.changedTouches.length!==1||navigating) return;
    const touch=event.changedTouches[0];
    const dx=touch.clientX-start.x;
    const dy=touch.clientY-start.y;
    const elapsed=performance.now()-start.time;
    if(elapsed>SWIPE_MAX_MS||Math.abs(dx)<SWIPE_MIN_X||Math.abs(dx)<Math.abs(dy)*1.15) return;
"""
if old_end_check not in text:
    raise SystemExit('touchend check not found')
text = text.replace(old_end_check, new_end_check, 1)

old_apply = """    applyPage(url).catch(()=>{ location.href=url.href; });
  },{passive:false});
"""
new_apply = """    applyPage(url,{transitionDirection:direction}).catch(()=>{ location.href=url.href; });
  },{passive:false});
"""
if old_apply not in text:
    raise SystemExit('swipe applyPage call not found')
text = text.replace(old_apply, new_apply, 1)

js_path.write_text(text)

changed = 0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for path in Path('.').glob(pattern):
        html = path.read_text()
        newer = html.replace('site.js?v=20260919-12','site.js?v=20260919-13')
        if newer != html:
            path.write_text(newer)
            changed += 1
if changed == 0:
    raise SystemExit('no HTML site.js version references updated')
print(f'updated site.js and {changed} HTML files')
# trigger workflow after workflow definition exists
