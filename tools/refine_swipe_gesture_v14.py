from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()

def one(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' not found')
    s=s.replace(old,new,1)

# Let swipe navigation hand the small finger-follow offset into the page transition.
one(
"const applyPage=async(url,{historyMode='push',preserveScrollY=null,transitionDirection=0}={})=>{",
"const applyPage=async(url,{historyMode='push',preserveScrollY=null,transitionDirection=0,gestureOffset=0}={})=>{",
'applyPage signature')

one(
"""      const shift=transitionDirection>0?-18:18;
      await animateMain(currentMain,[
        {transform:'translate3d(0,0,0)',opacity:1},
        {transform:`translate3d(${shift}px,0,0)`,opacity:.72}
      ],{duration:115,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});
""",
"""      const shift=transitionDirection>0?-18:18;
      const startShift=transitionDirection?Math.max(-18,Math.min(18,Number(gestureOffset)||0)):0;
      currentMain.style.willChange='transform, opacity';
      await animateMain(currentMain,[
        {transform:`translate3d(${startShift}px,0,0)`,opacity:1},
        {transform:`translate3d(${shift}px,0,0)`,opacity:.9}
      ],{duration:105,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});
""",
'outgoing animation')

one(
"""        await animateMain(incomingMain,[
          {transform:`translate3d(${incomingShift}px,0,0)`,opacity:.72},
          {transform:'translate3d(0,0,0)',opacity:1}
        ],{duration:190,easing:'cubic-bezier(.2,.72,.22,1)',fill:'both'});
      }
""",
"""        await animateMain(incomingMain,[
          {transform:`translate3d(${incomingShift}px,0,0)`,opacity:.9},
          {transform:'translate3d(0,0,0)',opacity:1}
        ],{duration:175,easing:'cubic-bezier(.2,.72,.22,1)',fill:'both'});
      }
      incomingMain.style.willChange='';
      setTimeout(()=>warmSwipeNeighbors(),40);
""",
'incoming animation')

one(
"""  const SWIPE_MIN_X=56;
  const SWIPE_MAX_MS=1200;
  let pageSwipeStart=null;
""",
"""  const SWIPE_MIN_X=56;
  const SWIPE_FLICK_MIN_X=26;
  const SWIPE_FLICK_MAX_MS=420;
  const SWIPE_FLICK_MIN_VX=.28;
  const SWIPE_MAX_MS=1200;
  const SWIPE_FOLLOW_MAX=18;
  const SWIPE_FOLLOW_FACTOR=.28;
  let pageSwipeStart=null;

  const resetSwipeVisual=(animate=true)=>{
    const main=document.querySelector('main');
    if(!main) return;
    if(!animate||typeof main.animate!=='function'){
      main.style.transform='';
      main.style.willChange='';
      return;
    }
    const computed=main.style.transform||'translate3d(0,0,0)';
    main.style.transform='';
    main.style.willChange='';
    try{
      main.animate([
        {transform:computed},
        {transform:'translate3d(0,0,0)'}
      ],{duration:145,easing:'cubic-bezier(.2,.75,.25,1)'});
    }catch(_e){}
  };
""",
'swipe constants')

one(
"""    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang,locked:false,warmedDirection:0};
""",
"""    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang,locked:false,warmedDirection:0,followOffset:0};
""",
'touchstart state')

one(
"""    event.preventDefault();
    const direction=dx<0?1:-1;
    if(direction!==start.warmedDirection){
""",
"""    event.preventDefault();
    const follow=Math.max(-SWIPE_FOLLOW_MAX,Math.min(SWIPE_FOLLOW_MAX,dx*SWIPE_FOLLOW_FACTOR));
    start.followOffset=follow;
    const main=document.querySelector('main');
    if(main){
      main.style.willChange='transform';
      main.style.transform=`translate3d(${follow}px,0,0)`;
    }

    const direction=dx<0?1:-1;
    if(direction!==start.warmedDirection){
""",
'touchmove follow')

one(
"""  document.addEventListener('touchcancel',()=>{ pageSwipeStart=null; },{passive:true});
""",
"""  document.addEventListener('touchcancel',()=>{
    if(pageSwipeStart?.locked) resetSwipeVisual(true);
    pageSwipeStart=null;
  },{passive:true});
""",
'touchcancel')

old_end="""  document.addEventListener('touchend',event=>{
    const start=pageSwipeStart;
    pageSwipeStart=null;
    if(!start||!start.locked||event.changedTouches.length!==1||navigating) return;
    const touch=event.changedTouches[0];
    const dx=touch.clientX-start.x;
    const dy=touch.clientY-start.y;
    const elapsed=performance.now()-start.time;
    if(elapsed>SWIPE_MAX_MS||Math.abs(dx)<SWIPE_MIN_X||Math.abs(dx)<Math.abs(dy)*1.15) return;

    const current=normalizedPath();
    if(current!==start.path) return;
    const pages=swipePageOrder[start.lang];
    const index=pages.indexOf(current);
    if(index<0) return;
    const direction=dx<0?1:-1;
    const targetPath=pages[(index+direction+pages.length)%pages.length];
    const url=new URL(root(targetPath),location.origin);
    event.preventDefault();
    saveCurrentScroll();
    applyPage(url,{transitionDirection:direction}).catch(()=>{ location.href=url.href; });
  },{passive:false});
"""
new_end="""  document.addEventListener('touchend',event=>{
    const start=pageSwipeStart;
    pageSwipeStart=null;
    if(!start||!start.locked||event.changedTouches.length!==1||navigating){
      if(start?.locked) resetSwipeVisual(true);
      return;
    }
    const touch=event.changedTouches[0];
    const dx=touch.clientX-start.x;
    const dy=touch.clientY-start.y;
    const elapsed=Math.max(1,performance.now()-start.time);
    const vx=dx/elapsed;
    const horizontal=Math.abs(dx)>=Math.abs(dy)*1.15;
    const distanceCommit=Math.abs(dx)>=SWIPE_MIN_X;
    const flickCommit=Math.abs(dx)>=SWIPE_FLICK_MIN_X&&elapsed<=SWIPE_FLICK_MAX_MS&&Math.abs(vx)>=SWIPE_FLICK_MIN_VX;
    if(elapsed>SWIPE_MAX_MS||!horizontal||(!distanceCommit&&!flickCommit)){
      resetSwipeVisual(true);
      return;
    }

    const current=normalizedPath();
    if(current!==start.path){ resetSwipeVisual(false); return; }
    const pages=swipePageOrder[start.lang];
    const index=pages.indexOf(current);
    if(index<0){ resetSwipeVisual(true); return; }
    const direction=dx<0?1:-1;
    const targetPath=pages[(index+direction+pages.length)%pages.length];
    const url=new URL(root(targetPath),location.origin);
    event.preventDefault();
    saveCurrentScroll();
    applyPage(url,{transitionDirection:direction,gestureOffset:start.followOffset}).catch(()=>{ location.href=url.href; });
  },{passive:false});
"""
one(old_end,new_end,'touchend block')

needle="""  const swipePageOrder={
    zh:['/','/about.html','/team.html','/research.html','/publications.html','/join.html','/contact.html'],
    en:['/en/','/en/about.html','/en/team.html','/en/research.html','/en/publications.html','/en/join.html','/en/contact.html']
  };
"""
replacement=needle+"""
  const warmSwipeNeighbors=()=>{
    if(navigator.connection&&navigator.connection.saveData) return;
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    const pages=swipePageOrder[lang];
    const index=pages.indexOf(path);
    if(index<0) return;
    [-1,1].forEach(offset=>{
      const target=pages[(index+offset+pages.length)%pages.length];
      fetchPage(new URL(root(target),location.origin)).catch(()=>{});
    });
  };
  setTimeout(warmSwipeNeighbors,420);
"""
one(needle,replacement,'swipe order')

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for hp in Path('.').glob(pattern):
        h=hp.read_text()
        n=h.replace('site.js?v=20260919-13','site.js?v=20260919-14')
        if n!=h:
            hp.write_text(n)
            changed+=1
if not changed:
    raise SystemExit('no site.js v13 refs found')
print('updated gesture refinement and',changed,'html files')
# trigger after workflow creation
