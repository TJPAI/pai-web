from pathlib import Path

js_path = Path('assets/js/site.js')
text = js_path.read_text()

def replace_once(old, new, label):
    global text
    if old not in text:
        raise SystemExit(f'{label} not found')
    text = text.replace(old, new, 1)

replace_once(
    "const applyPage=async(url,{historyMode='push',preserveScrollY=null}={})=>{",
    "const applyPage=async(url,{historyMode='push',preserveScrollY=null,transitionDirection=0}={})=>{",
    'applyPage signature'
)

replace_once(
    "      if(!currentMain||!nextMain) throw new Error('page shell unavailable');\n",
    """      if(!currentMain||!nextMain) throw new Error('page shell unavailable');

      const reduceMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
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
""",
    'animation insertion point'
)

replace_once(
    "      currentMain.replaceWith(document.importNode(nextMain,true));\n",
    "      const incomingMain=document.importNode(nextMain,true);\n      currentMain.replaceWith(incomingMain);\n",
    'main replacement'
)

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
replace_once(old_scroll, new_scroll, 'scroll block')

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
replace_once(old_touchstart_tail, new_touchstart_tail, 'touchstart tail')

replace_once(
    "    if(!start||event.changedTouches.length!==1||navigating) return;\n",
    "    if(!start||!start.locked||event.changedTouches.length!==1||navigating) return;\n",
    'touchend lock check'
)

old_swipe_apply = """    event.preventDefault();
    saveCurrentScroll();
    applyPage(url).catch(()=>{ location.href=url.href; });
  },{passive:false});
"""
new_swipe_apply = """    event.preventDefault();
    saveCurrentScroll();
    applyPage(url,{transitionDirection:direction}).catch(()=>{ location.href=url.href; });
  },{passive:false});
"""
# Use the last occurrence so normal click navigation remains unchanged.
pos = text.rfind(old_swipe_apply)
if pos < 0:
    raise SystemExit('swipe applyPage block not found')
text = text[:pos] + new_swipe_apply + text[pos+len(old_swipe_apply):]

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
