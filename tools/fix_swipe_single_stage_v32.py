from pathlib import Path
import re

p=Path('assets/js/site.js')
s=p.read_text()

# Replace the swipe preview/stage machinery up to the transform animator.
start=s.index("  const cleanupStaleSwipePreviews=()=>{")
end=s.index("  const animateElementTransform=", start)
new=r'''  const restoreLiveSwipeSurface=()=>{
    const surface=document.querySelector('.page-surface');
    if(surface){
      surface.style.visibility='';
      surface.style.transform='';
      surface.style.willChange='';
    }
  };
  const cleanupStaleSwipePreviews=()=>{
    document.querySelectorAll('[data-pai-swipe-preview]').forEach(node=>node.remove());
    restoreLiveSwipeSurface();
  };
  const enforceSinglePageFooter=()=>{
    const surface=document.querySelector('.page-surface');
    if(!surface) return;
    document.querySelectorAll('.site-footer').forEach(footer=>{
      if(!surface.contains(footer)&&!footer.closest('[data-pai-swipe-preview]')) footer.remove();
    });
    const footers=[...surface.querySelectorAll('.site-footer')];
    footers.slice(1).forEach(footer=>footer.remove());
  };
  cleanupStaleSwipePreviews();
  enforceSinglePageFooter();

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

  const stripPreviewIds=node=>{
    if(!node) return;
    node.removeAttribute?.('id');
    node.querySelectorAll?.('[id]').forEach(child=>child.removeAttribute('id'));
  };

  /* Keep both pages in one fixed compositing stage. Safari no longer has to animate
     a document-flow page and a promoted fixed preview in separate render layers. */
  const ensureSwipeStage=()=>{
    if(swipePreview?.shell?.isConnected&&swipePreview.current) return swipePreview;
    document.querySelectorAll('[data-pai-swipe-preview]').forEach(node=>node.remove());
    const live=document.querySelector('.page-surface');
    if(!live) return null;
    const shell=document.createElement('div');
    shell.setAttribute('aria-hidden','true');
    shell.setAttribute('data-pai-swipe-preview','');
    Object.assign(shell.style,{
      position:'fixed',inset:'0',overflow:'hidden',pointerEvents:'none',
      zIndex:'12',contain:'layout paint',background:'transparent'
    });
    const current=document.importNode(live,true);
    stripPreviewIds(current);
    const rect=live.getBoundingClientRect();
    Object.assign(current.style,{
      position:'absolute',top:`${rect.top}px`,left:'0',width:'100%',minHeight:`${Math.max(rect.height,innerHeight)}px`,
      margin:'0',willChange:'transform',pointerEvents:'none',
      background:getComputedStyle(document.body).backgroundColor||'#fff',
      transform:'translate3d(0,0,0)'
    });
    shell.appendChild(current);
    document.body.appendChild(shell);
    live.style.visibility='hidden';
    swipePreview={shell,current,surface:null,main:null,url:null,direction:0,targetScroll:0,previewScroll:0};
    return swipePreview;
  };

  const destroySwipePreview=(resetCurrent=true)=>{
    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();
    document.querySelectorAll('[data-pai-swipe-preview]').forEach(node=>node.remove());
    swipePreview=null;
    if(resetCurrent) restoreLiveSwipeSurface();
  };

  const buildSwipePreview=(url,direction,html)=>{
    if(!pageSwipeStart||pageSwipeStart.direction!==direction) return null;
    const stage=ensureSwipeStage();
    if(!stage||!stage.shell.isConnected) return null;
    const next=new DOMParser().parseFromString(html,'text/html');
    const nextSurface=next.querySelector('.page-surface');
    const nextMain=nextSurface?.querySelector('main');
    if(!nextSurface||!nextMain) return null;

    if(stage.surface?.isConnected) stage.surface.remove();
    const previewSurface=document.importNode(nextSurface,true);
    const previewMain=previewSurface.querySelector('main');
    stripPreviewIds(previewSurface);
    previewSurface.querySelectorAll('img[src]').forEach(img=>{
      try{ img.src=new URL(img.getAttribute('src'),url.href).href; }catch(_e){}
    });
    previewSurface.querySelectorAll('source[srcset],img[srcset]').forEach(node=>{
      const raw=node.getAttribute('srcset');
      if(!raw) return;
      const resolved=raw.split(',').map(part=>{
        const bits=part.trim().split(/\s+/);
        try{ bits[0]=new URL(bits[0],url.href).href; }catch(_e){}
        return bits.join(' ');
      }).join(', ');
      node.setAttribute('srcset',resolved);
    });
    const header=document.querySelector('.site-header');
    const mainDocumentTop=Math.max(0,header?.getBoundingClientRect().bottom||0);
    const targetPath=normalizedPath(url.pathname);
    const targetScroll=rememberedPageScroll(targetPath);
    Object.assign(previewSurface.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',
      margin:'0',willChange:'transform',pointerEvents:'none',
      background:getComputedStyle(document.body).backgroundColor||'#fff',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
    stage.shell.appendChild(previewSurface);
    const previewMaxScroll=Math.max(0,mainDocumentTop+previewSurface.scrollHeight-innerHeight);
    const previewScroll=Math.min(targetScroll,previewMaxScroll);
    previewSurface.style.top=`${mainDocumentTop-previewScroll}px`;
    Object.assign(stage,{surface:previewSurface,main:previewMain,url,direction,targetScroll,previewScroll});
    return stage;
  };

  const ensureSwipePreview=(direction)=>{
    const start=pageSwipeStart;
    if(!start) return Promise.resolve(null);
    const stage=ensureSwipeStage();
    if(!stage) return Promise.resolve(null);
    if(stage.surface&&stage.direction===direction) return Promise.resolve(stage);
    if(stage.surface?.isConnected) stage.surface.remove();
    stage.surface=null;
    stage.main=null;
    stage.url=null;
    start.direction=direction;
    stage.direction=direction;
    const targetPath=swipeTargetFor(start.path,start.lang,direction);
    if(!targetPath) return Promise.resolve(null);
    const url=new URL(root(targetPath),location.origin);
    return fetchPage(url).then(html=>buildSwipePreview(url,direction,html)).catch(()=>null);
  };

  const positionSwipePages=dx=>{
    const start=pageSwipeStart;
    if(!start) return;
    const stage=ensureSwipeStage();
    if(!stage) return;
    const width=Math.max(1,innerWidth);
    const bounded=Math.max(-width,Math.min(width,dx));
    const direction=bounded<0?1:-1;
    stage.current.style.transform=`translate3d(${bounded}px,0,0)`;
    if(!stage.surface||stage.direction!==direction) return;
    const incoming=bounded+(direction>0?width:-width);
    stage.surface.style.transform=`translate3d(${incoming}px,0,0)`;
  };

'''
s=s[:start]+new+s[end:]

# Settle and commit must animate the current snapshot, not the hidden live page.
s=s.replace("    const current=document.querySelector('.page-surface');\n    const preview=swipePreview;\n    if(!current){ destroySwipePreview(); return; }\n    const currentFrom=current.style.transform||'translate3d(0,0,0)';",
            "    const preview=swipePreview;\n    const current=preview?.current;\n    if(!current){ destroySwipePreview(); return; }\n    const currentFrom=current.style.transform||'translate3d(0,0,0)';",1)
s=s.replace("    const current=document.querySelector('.page-surface');\n    const preview=swipePreview;\n    const start=pageSwipeStart;\n    if(!current||!preview||!start){ destroySwipePreview(); return; }",
            "    const preview=swipePreview;\n    const current=preview?.current;\n    const start=pageSwipeStart;\n    if(!current||!preview?.surface||!start){ destroySwipePreview(); return; }",1)

# Version bump all static pages.
count=0
for f in Path('.').rglob('*.html'):
    if any(part in {'.git','node_modules'} for part in f.parts):
        continue
    text=f.read_text()
    text=text.replace('site.js?v=20260919-31','site.js?v=20260919-32')
    f.write_text(text)
    count+=1
p.write_text(s)
print('single-stage swipe installed; html pages',count)
