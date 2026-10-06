(function(){
  'use strict';

  const clearHomeLogo=()=>{
    document.querySelectorAll('.home-hero .hero-art').forEach(host=>{
      host.replaceChildren();
      host.removeAttribute('data-pai-logo-static');
      host.classList.remove('pai-logo-motion-host','pai-logo-motion-ready','pai-logo-motion-exit','pai-logo-motion-hidden');
    });
  };

  window.initHomeLogo=clearHomeLogo;

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',clearHomeLogo,{once:true});
  else clearHomeLogo();

  // Lightweight navigation can reinsert homepage markup; keep the former logo slot empty.
  new MutationObserver(clearHomeLogo).observe(document.body,{childList:true,subtree:true});
})();
