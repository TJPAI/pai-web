from pathlib import Path

js_path=Path('assets/js/site.js')
text=js_path.read_text()

def replace_once(old,new,label):
    global text
    if old not in text:
        raise SystemExit(f'{label} not found')
    text=text.replace(old,new,1)

# Softer page transition: less opacity change, slightly more horizontal continuity.
replace_once(
"""      const shift=transitionDirection>0?-18:18;
      await animateMain(currentMain,[
        {transform:'translate3d(0,0,0)',opacity:1},
        {transform:`translate3d(${shift}px,0,0)`,opacity:.72}
      ],{duration:115,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});
""",
"""      const shift=transitionDirection>0?-26:26;
      const currentTransform=currentMain.style.transform||'translate3d(0,0,0)';
      await animateMain(currentMain,[
        {transform:currentTransform,opacity:1},
        {transform:`translate3d(${shift}px,0,0)`,opacity:.9}
      ],{duration:105,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});
""",
'outgoing transition')

replace_once(
"""        const incomingShift=transitionDirection>0?18:-18;
        await new Promise(resolve=>requestAnimationFrame(resolve));
        await animateMain(incomingMain,[
          {transform:`translate3d(${incomingShift}px,0,0)`,opacity:.72},
          {transform:'translate3d(0,0,0)',opacity:1}
        ],{duration:190,easing:'cubic-bezier(.2,.72,.22,1)',fill:'both'});
""",
"""        const incomingShift=transitionDirection>0?24:-24;
        await new Promise(resolve=>requestAnimationFrame(resolve));
        await animateMain(incomingMain,[
          {transform:`translate3d(${incomingShift}px,0,0)`,opacity:.9},
          {transform:'translate3d(0,0,0)',opacity:1}
        ],{duration:175,easing:'cubic-bezier(.2,.72,.22,1)',fill:'both'});
""",
'incoming transition')

# Add tuned gesture constants.
replace_once(
"""  const SWIPE_EDGE_GUARD=32;
  const SWIPE_MIN_X=56;
  const SWIPE_MAX_MS=1200;
  let pageSwipeStart=null;
""",
"""  const SWIPE_EDGE_GUARD=32;
  const SWIPE_MIN_X=52;
  const SWIPE_FAST_MIN_X=28;
  const SWIPE_FAST_VELOCITY=.42;
  const SWIPE_MAX_MS=1200;
  const SWIPE_FOLLOW_MAX=18;
  const SWIPE_SETTLE_MS=140;
  let pageSwipeStart=null;

  const swipeMain=()=>document.querySelector('main');
  const clearSwipeVisual=(animate=true)=>{
    const main=swipeMain();
    if(!main) return;
    const reduceMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(animate&&!reduceMotion&&typeof main.animate==='function'){
      const from=main.style.transform||'translate3d(0,0,0)';
      try{
        const animation=main.animate([
          {transform:from},
          {transform:'translate3d(0,0,0)'}
        ],{duration:SWIPE_SETTLE_MS,easing:'cubic-bezier(.2,.72,.22,1)'});
        animation.finished.catch(()=>{}).finally(()=>{ main.style.transform=''; main.style.willChange=''; });
        return;
      }catch(_e){}
    }
    main.style.transform='';
    main.style.willChange='';
  };
""",
'gesture constants')

replace_once(
"""    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang,locked:false,warmedDirection:0};
""",
"""    const now=performance.now();
    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:now,path,lang,locked:false,warmedDirection:0,lastX:touch.clientX,lastTime:now,velocityX:0};
""",
'touchstart state')

# Replace touchmove body after lock with follow-finger behavior and velocity tracking.
old_move="""    event.preventDefault();
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
"""
new_move="""    event.preventDefault();
    const now=performance.now();
    const dt=Math.max(1,now-start.lastTime);
    start.velocityX=(touch.clientX-start.lastX)/dt;
    start.lastX=touch.clientX;
    start.lastTime=now;

    const follow=Math.max(-SWIPE_FOLLOW_MAX,Math.min(SWIPE_FOLLOW_MAX,dx*.18));
    const main=swipeMain();
    if(main){
      main.style.willChange='transform';
      main.style.transform=`translate3d(${follow}px,0,0)`;
    }

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
"""
replace_once(old_move,new_move,'touchmove follow')

# Touch cancel should also settle visual state.
replace_once(
"""  document.addEventListener('touchcancel',()=>{ pageSwipeStart=null; },{passive:true});
""",
"""  document.addEventListener('touchcancel',()=>{
    pageSwipeStart=null;
    clearSwipeVisual(true);
  },{passive:true});
""",
'touchcancel')

# Replace touchend qualification with distance + velocity and rebound on failure.
old_end="""    const elapsed=performance.now()-start.time;
    if(elapsed>SWIPE_MAX_MS||Math.abs(dx)<SWIPE_MIN_X||Math.abs(dx)<Math.abs(dy)*1.15) return;

    const current=normalizedPath();
"""
new_end="""    const elapsed=performance.now()-start.time;
    const horizontalEnough=Math.abs(dx)>=SWIPE_MIN_X;
    const fastEnough=Math.abs(dx)>=SWIPE_FAST_MIN_X&&Math.abs(start.velocityX)>=SWIPE_FAST_VELOCITY;
    if(elapsed>SWIPE_MAX_MS||Math.abs(dx)<Math.abs(dy)*1.15||(!horizontalEnough&&!fastEnough)){
      clearSwipeVisual(true);
      return;
    }

    const current=normalizedPath();
"""
replace_once(old_end,new_end,'touchend qualification')

# If state changed unexpectedly, restore visual.
replace_once(
"""    if(current!==start.path) return;
""",
"""    if(current!==start.path){ clearSwipeVisual(true); return; }
""",
'touchend path guard')
replace_once(
"""    if(index<0) return;
""",
"""    if(index<0){ clearSwipeVisual(true); return; }
""",
'touchend index guard')

# Add neighbor prefetch after swipe helpers, and initial invocation.
needle="""  document.addEventListener('touchend',event=>{
"""
insert="""  const warmSwipeNeighbors=()=>{
    if(navigator.connection&&navigator.connection.saveData) return;
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    const pages=swipePageOrder[lang];
    const index=pages.indexOf(path);
    if(index<0) return;
    [-1,1].forEach(offset=>{
      const targetPath=pages[(index+offset+pages.length)%pages.length];
      fetchPage(new URL(root(targetPath),location.origin)).catch(()=>{});
    });
  };
  setTimeout(warmSwipeNeighbors,160);

  document.addEventListener('touchend',event=>{
"""
replace_once(needle,insert,'neighbor prefetch insertion')

# Warm new neighbors after every successful page swap.
replace_once(
"""      setTimeout(()=>warmNavigation(),80);
""",
"""      setTimeout(()=>{
        warmNavigation();
        if(typeof warmSwipeNeighbors==='function') warmSwipeNeighbors();
      },80);
""",
'post navigation warm')

js_path.write_text(text)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for path in Path('.').glob(pattern):
        html=path.read_text()
        newer=html.replace('site.js?v=20260919-13','site.js?v=20260919-14')
        if newer!=html:
            path.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no HTML site.js version references updated')
print(f'updated site.js and {changed} HTML files')
