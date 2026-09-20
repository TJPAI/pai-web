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
    return `${prefix}/assets/media/pai-logo-motion.mp4?v=20260920-01`;
  };
  let scheduled=false;
  const init=()=>{
    scheduled=false;
    if(!isHome()) return;
    const host=document.querySelector('.home-hero .hero-art');
    if(!host||host.dataset.paiLogoMotion==='1') return;
    host.dataset.paiLogoMotion='1';
    host.classList.add('pai-logo-motion-host');
    const video=document.createElement('video');
    video.className='pai-logo-motion';
    video.muted=true; video.defaultMuted=true; video.playsInline=true;
    video.setAttribute('playsinline',''); video.setAttribute('webkit-playsinline','');
    video.preload='auto'; video.setAttribute('aria-hidden','true'); video.src=mediaUrl();
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(reduced){
      video.addEventListener('loadedmetadata',()=>{try{video.currentTime=Math.max(0,(video.duration||5)-0.04);}catch(_e){}},{once:true});
      video.addEventListener('seeked',()=>{host.replaceChildren(video);},{once:true});
    }else{
      video.autoplay=true;
      video.addEventListener('canplay',()=>{host.replaceChildren(video);video.play().catch(()=>{});},{once:true});
    }
  };
  const schedule=()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(init);};
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',schedule,{once:true}); else schedule();
  new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});
  addEventListener('popstate',schedule);
})();
