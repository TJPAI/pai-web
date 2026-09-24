(function(){
  'use strict';
  const normalizedPath=()=>{
    let path=location.pathname||'/';
    if(location.hostname==='tjpai.github.io'&&path.startsWith('/pai-web')) path=path.slice('/pai-web'.length)||'/';
    return path;
  };
  const isHome=()=>['/','/index.html','/en/','/en/index.html'].includes(normalizedPath());
  const mediaUrl=()=>{
    const prefix=location.hostname==='tjpai.github.io'?'/pai-web':'';
    return `${prefix}/assets/media/pai-logo-one-stroke-5s.svg?v=20260924-01`;
  };
  let scheduled=false;
  const init=()=>{
    scheduled=false;
    if(!isHome()) return;
    const host=document.querySelector('.home-hero .hero-art');
    if(!host||host.dataset.paiLogoMotion==='1') return;
    host.dataset.paiLogoMotion='1';
    host.classList.add('pai-logo-motion-host');

    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    const logo=document.createElement('img');
    logo.className='pai-logo-motion';
    logo.alt='';
    logo.setAttribute('aria-hidden','true');
    logo.decoding='async';
    logo.src=mediaUrl();
    host.replaceChildren(logo);

    if(reduced) return;

    window.setTimeout(()=>{
      if(!isHome()) return;
      host.classList.add('pai-logo-motion-exit');
      window.setTimeout(()=>host.classList.add('pai-logo-motion-hidden'),760);
    },5450);
  };
  const schedule=()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(init);};
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',schedule,{once:true}); else schedule();
  new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});
  addEventListener('popstate',schedule);
})();
