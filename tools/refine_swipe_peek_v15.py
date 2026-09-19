from pathlib import Path

js_path=Path('assets/js/site.js')
text=js_path.read_text()
start_marker="  /* Touch page navigation for the seven top-level pages."
end_marker="  const responseFor=async url=>{"
start=text.find(start_marker)
end=text.find(end_marker,start)
if start<0 or end<0:
    raise SystemExit('swipe block markers not found')

block=r'''  /* Touch page navigation for the seven top-level pages.
     Horizontal drags behave like a native pager: the adjacent page is already visible
     underneath the finger, while edge swipes stay reserved for Safari history gestures. */
  const swipePageOrder={
    zh:['/','/about.html','/team.html','/research.html','/publications.html','/join.html','/contact.html'],
    en:['/en/','/en/about.html','/en/team.html','/en/research.html','/en/publications.html','/en/join.html','/en/contact.html']
  };

  const SWIPE_EDGE_GUARD=32;
  const SWIPE_MIN_X=58;
  const SWIPE_FLICK_MIN_X=28;
  const SWIPE_FLICK_MAX_MS=420;
  const SWIPE_FLICK_MIN_VX=.30;
  const SWIPE_MAX_MS=1200;
  const SWIPE_SETTLE_MS=220;
  let pageSwipeStart=null;
  let swipePreview=null;

  const swipeBlockedTarget=target=>!!(target?.closest&&target.closest(
    'a,button,input,textarea,select,option,label,[contenteditable="true"],[role="button"],[data-no-swipe]'
  ));

  const swipeTargetFor=(path,lang,direction)=>{
    const pages=swipePageOrder[lang];
    const index=pages.indexOf(path);
    if(index<0) return null;
    return pages[(index+direction+pages.length)%pages.length];
  };

  const warmSwipeNeighbors=()=>{
    if(navigator.connection&&navigator.connection.saveData) return;
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    [-1,1].forEach(direction=>{
      const targetPath=swipeTargetFor(path,lang,direction);
      if(targetPath) fetchPage(new URL(root(targetPath),location.origin)).catch(()=>{});
    });
  };
  setTimeout(warmSwipeNeighbors,260);

  const destroySwipePreview=()=>{
    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();
    swipePreview=null;
    const main=document.querySelector('main');
    if(main){
      main.style.transform='';
      main.style.willChange='';
    }
  };

  const buildSwipePreview=(url,direction,html)=>{
    if(!pageSwipeStart||pageSwipeStart.direction!==direction) return null;
    const next=new DOMParser().parseFromString(html,'text/html');
    const nextMain=next.querySelector('main');
    if(!nextMain) return null;

    const shell=document.createElement('div');
    shell.setAttribute('aria-hidden','true');
    Object.assign(shell.style,{
      position:'fixed',inset:'0',overflow:'hidden',pointerEvents:'none',
      zIndex:'12',contain:'layout paint',background:'transparent'
    });
    const previewMain=document.importNode(nextMain,true);
    previewMain.removeAttribute('id');
    previewMain.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));
    previewMain.querySelectorAll('img[src]').forEach(img=>{
      try{ img.src=new URL(img.getAttribute('src'),url.href).href; }catch(_e){}
    });
    previewMain.querySelectorAll('source[srcset],img[srcset]').forEach(node=>{
      const raw=node.getAttribute('srcset');
      if(!raw) return;
      const resolved=raw.split(',').map(part=>{
        const bits=part.trim().split(/\s+/);
        try{ bits[0]=new URL(bits[0],url.href).href; }catch(_e){}
        return bits.join(' ');
      }).join(', ');
      node.setAttribute('srcset',resolved);
    });
    Object.assign(previewMain.style,{
      position:'absolute',top:'0',left:'0',width:'100%',minHeight:'100vh',
      margin:'0',willChange:'transform',pointerEvents:'none',
      background:getComputedStyle(document.body).backgroundColor||'#fff',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
    shell.appendChild(previewMain);
    document.body.appendChild(shell);
    swipePreview={shell,main:previewMain,url,direction};
    return swipePreview;
  };

  const ensureSwipePreview=(direction)=>{
    const start=pageSwipeStart;
    if(!start) return Promise.resolve(null);
    if(swipePreview&&swipePreview.direction===direction) return Promise.resolve(swipePreview);
    if(swipePreview) destroySwipePreview();
    start.direction=direction;
    const targetPath=swipeTargetFor(start.path,start.lang,direction);
    if(!targetPath) return Promise.resolve(null);
    const url=new URL(root(targetPath),location.origin);
    return fetchPage(url).then(html=>buildSwipePreview(url,direction,html)).catch(()=>null);
  };

  const positionSwipePages=dx=>{
    const start=pageSwipeStart;
    const preview=swipePreview;
    if(!start||!preview) return;
    const width=Math.max(1,innerWidth);
    const bounded=Math.max(-width,Math.min(width,dx));
    const direction=preview.direction;
    if((direction>0&&bounded>0)||(direction<0&&bounded<0)) return;
    const current=document.querySelector('main');
    if(current){
      current.style.willChange='transform';
      current.style.transform=`translate3d(${bounded}px,0,0)`;
    }
    const incoming=bounded+(direction>0?width:-width);
    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;
  };

  const animateElementTransform=(node,from,to,duration=SWIPE_SETTLE_MS)=>new Promise(resolve=>{
    if(!node){ resolve(); return; }
    if(matchMedia('(prefers-reduced-motion: reduce)').matches||typeof node.animate!=='function'){
      node.style.transform=to;
      resolve();
      return;
    }
    try{
      const animation=node.animate([{transform:from},{transform:to}],{
        duration,easing:'cubic-bezier(.22,.72,.22,1)',fill:'forwards'
      });
      animation.finished.catch(()=>{}).finally(resolve);
    }catch(_e){
      node.style.transform=to;
      resolve();
    }
  });

  const settleSwipeBack=async()=>{
    const current=document.querySelector('main');
    const preview=swipePreview;
    if(!current||!preview){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=current.style.transform||'translate3d(0,0,0)';
    const incomingFrom=preview.main.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;
    await Promise.all([
      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',165),
      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,165)
    ]);
    destroySwipePreview();
  };

  const commitSwipe=async(direction)=>{
    const current=document.querySelector('main');
    const preview=swipePreview;
    const start=pageSwipeStart;
    if(!current||!preview||!start){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=current.style.transform||'translate3d(0,0,0)';
    const incomingFrom=preview.main.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;
    const targetUrl=preview.url;
    await Promise.all([
      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,205),
      animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',205)
    ]);
    try{
      await applyPage(targetUrl,{transitionDirection:0});
    }finally{
      destroySwipePreview();
      setTimeout(warmSwipeNeighbors,60);
    }
  };

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
    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang,locked:false,direction:0,lastDx:0};
  },{passive:true});

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
    start.lastDx=dx;
    const direction=dx<0?1:-1;
    if(direction!==start.direction){
      ensureSwipePreview(direction).then(()=>{
        if(pageSwipeStart===start) positionSwipePages(start.lastDx);
      });
    }else{
      positionSwipePages(dx);
    }
  },{passive:false});

  document.addEventListener('touchcancel',()=>{
    const hadLocked=pageSwipeStart?.locked;
    pageSwipeStart=null;
    if(hadLocked) settleSwipeBack();
    else destroySwipePreview();
  },{passive:true});

  document.addEventListener('touchend',event=>{
    const start=pageSwipeStart;
    if(!start||!start.locked||event.changedTouches.length!==1||navigating){
      pageSwipeStart=null;
      if(start?.locked) settleSwipeBack();
      else destroySwipePreview();
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
    const direction=dx<0?1:-1;

    if(elapsed>SWIPE_MAX_MS||!horizontal||(!distanceCommit&&!flickCommit)||!swipePreview||swipePreview.direction!==direction){
      pageSwipeStart=null;
      settleSwipeBack();
      return;
    }

    const current=normalizedPath();
    if(current!==start.path){
      pageSwipeStart=null;
      settleSwipeBack();
      return;
    }
    event.preventDefault();
    saveCurrentScroll();
    commitSwipe(direction).finally(()=>{ pageSwipeStart=null; });
  },{passive:false});

'''
text=text[:start]+block+text[end:]
js_path.write_text(text)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for path in Path('.').glob(pattern):
        html=path.read_text()
        newer=html.replace('site.js?v=20260919-14','site.js?v=20260919-15')
        if newer!=html:
            path.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no HTML site.js v14 references updated')
print(f'updated swipe pager and {changed} HTML files')
