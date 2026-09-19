#!/usr/bin/env python3
from pathlib import Path

path=Path('assets/js/site.js')
text=path.read_text(encoding='utf-8')
marker="  const responseFor=async url=>{"
if marker not in text:
    raise SystemExit('site.js insertion marker not found')
if 'const swipePageOrder=' in text:
    raise SystemExit('swipe navigation already present')

block=r'''  /* Touch page navigation for the seven top-level pages.
     Middle-screen horizontal swipes navigate; edge swipes stay reserved for Safari history gestures. */
  const swipePageOrder={
    zh:['/','/about.html','/team.html','/research.html','/publications.html','/join.html','/contact.html'],
    en:['/en/','/en/about.html','/en/team.html','/en/research.html','/en/publications.html','/en/join.html','/en/contact.html']
  };
  const SWIPE_EDGE_GUARD=32;
  const SWIPE_MIN_X=72;
  const SWIPE_MAX_MS=700;
  let pageSwipeStart=null;

  const swipeBlockedTarget=target=>!!(target?.closest&&target.closest(
    'a,button,input,textarea,select,option,label,[contenteditable="true"],[role="button"],[data-no-swipe]'
  ));

  document.addEventListener('touchstart',event=>{
    if(event.touches.length!==1){ pageSwipeStart=null; return; }
    const touch=event.touches[0];
    if(touch.clientX<=SWIPE_EDGE_GUARD||touch.clientX>=innerWidth-SWIPE_EDGE_GUARD||swipeBlockedTarget(event.target)){
      pageSwipeStart=null;
      return;
    }
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    if(!swipePageOrder[lang].includes(path)){ pageSwipeStart=null; return; }
    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang};
  },{passive:true});

  document.addEventListener('touchend',event=>{
    const start=pageSwipeStart;
    pageSwipeStart=null;
    if(!start||event.changedTouches.length!==1||navigating) return;
    const touch=event.changedTouches[0];
    const dx=touch.clientX-start.x;
    const dy=touch.clientY-start.y;
    const elapsed=performance.now()-start.time;
    if(elapsed>SWIPE_MAX_MS||Math.abs(dx)<SWIPE_MIN_X||Math.abs(dx)<Math.abs(dy)*1.35) return;

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
    applyPage(url).catch(()=>{ location.href=url.href; });
  },{passive:false});

'''
text=text.replace(marker,block+marker,1)
path.write_text(text,encoding='utf-8')
