(function(){
  'use strict';

  const RETURN_KEY='pai-home-cta-return-v1';
  const TOP_KEY='pai-home-cta-target-top-v1';
  const cleanHref=value=>{
    try{
      const url=new URL(value,location.href);
      url.hash='';
      return url.href;
    }catch(_e){ return String(value||''); }
  };
  const readJson=key=>{
    try{ return JSON.parse(sessionStorage.getItem(key)||'null'); }catch(_e){ return null; }
  };
  const writeJson=(key,value)=>{
    try{ sessionStorage.setItem(key,JSON.stringify(value)); }catch(_e){}
  };
  const clearKey=key=>{
    try{ sessionStorage.removeItem(key); }catch(_e){}
  };
  const instantScroll=y=>{
    const root=document.documentElement;
    const previous=root.style.scrollBehavior;
    root.style.scrollBehavior='auto';
    window.scrollTo(0,Math.max(0,Number(y)||0));
    requestAnimationFrame(()=>{ root.style.scrollBehavior=previous; });
  };

  const forceTargetTop=()=>{
    const marker=readJson(TOP_KEY);
    if(!marker||marker.href!==cleanHref(location.href)) return;
    clearKey(TOP_KEY);
    instantScroll(0);
    requestAnimationFrame(()=>instantScroll(0));
  };

  const restoreReturnScroll=event=>{
    const marker=readJson(RETURN_KEY);
    if(!marker||marker.href!==cleanHref(location.href)) return;
    let backForward=!!event?.persisted;
    try{
      const nav=performance.getEntriesByType?.('navigation')?.[0];
      backForward=backForward||nav?.type==='back_forward';
    }catch(_e){}
    if(!backForward) return;
    clearKey(RETURN_KEY);
    requestAnimationFrame(()=>{
      instantScroll(marker.scrollY);
      requestAnimationFrame(()=>instantScroll(marker.scrollY));
    });
  };

  forceTargetTop();
  restoreReturnScroll();
  addEventListener('pageshow',restoreReturnScroll,{passive:true});

  document.addEventListener('click',event=>{
    if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    const link=event.target.closest&&event.target.closest('a[href]');
    if(!link) return;
    const main=document.querySelector('main');
    if(!main?.querySelector('.home-hero')) return;

    let url;
    try{ url=new URL(link.href,location.href); }catch(_e){ return; }
    if(url.origin!==location.origin||url.hash!=='#main-content') return;

    // These homepage CTAs must enter the destination exactly at page top while
    // browser Back returns to the precise scroll position the user left.
    const currentHref=cleanHref(location.href);
    const targetHref=cleanHref(url.href);
    const scrollY=Math.max(0,Math.round(window.scrollY||0));
    writeJson(RETURN_KEY,{href:currentHref,scrollY});
    writeJson(TOP_KEY,{href:targetHref});
    try{
      history.replaceState(Object.assign({},history.state||{},{pai:true,scrollY}),'',location.href);
    }catch(_e){}

    event.preventDefault();
    event.stopPropagation();
    url.hash='';
    location.assign(url.href);
  },true);
})();
