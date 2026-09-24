(function(){
  'use strict';

  const normalizedPath=()=>{
    let path=location.pathname||'/';
    if(location.hostname==='tjpai.github.io'&&path.startsWith('/pai-web')) path=path.slice('/pai-web'.length)||'/';
    return path;
  };
  const isHome=()=>['/','/index.html','/en/','/en/index.html'].includes(normalizedPath());

  const LOGO_PATH='M 93.8,88.8 L 597.8,88.9 L 632.9,91.0 L 666.3,97.3 L 697.8,108.2 L 727.2,124.0 L 750.1,141.1 L 775.3,166.1 L 792.4,189.0 L 808.3,218.4 L 817.7,244.6 L 823.5,272.1 L 825.5,307.1 L 822.2,341.7 L 813.6,374.2 L 800.0,404.5 L 781.5,432.8 L 757.5,458.6 L 730.5,480.3 L 701.1,496.4 L 659.1,510.9 L 607.7,517.1 L 266.0,517.8 L 225.1,520.4 L 197.8,527.0 L 167.7,541.3 L 140.6,562.5 L 121.6,584.4 L 109.8,603.5 L 98.8,629.0 L 93.1,650.6 L 89.7,679.2 L 90.0,900.3 L 92.1,929.5 L 96.3,951.7 L 103.5,972.7 L 114.6,992.1 L 129.4,1010.0 L 146.8,1025.4 L 165.8,1037.4 L 186.1,1046.4 L 213.2,1053.3 L 236.2,1055.2 L 270.4,1051.6 L 302.8,1042.7 L 333.1,1029.0 L 356.4,1012.8 L 899.6,453.2 L 917.7,439.4 L 942.6,427.1 L 969.6,419.7 L 998.1,416.6 L 1026.8,418.7 L 1059.3,427.1 L 1084.1,439.6 L 1102.3,453.7 L 1611.0,980.8 L 1649.8,1016.9 L 1673.7,1031.7 L 1699.2,1042.6 L 1726.1,1050.1 L 1748.8,1053.3 L 1766.0,1053.8 L 1788.5,1050.8 L 1809.9,1044.5 L 1829.8,1034.7 L 1857.1,1013.9 L 1878.8,987.1 L 1892.3,956.7 L 1898.3,923.2 L 1899.8,881.8 L 1899.8,89.8';

  let scheduled=false;
  let drawFrame=0;
  let exitTimer=0;
  let hideTimer=0;

  const clearMotion=()=>{
    if(drawFrame) cancelAnimationFrame(drawFrame);
    if(exitTimer) clearTimeout(exitTimer);
    if(hideTimer) clearTimeout(hideTimer);
    drawFrame=exitTimer=hideTimer=0;
  };

  const ease=t=>{
    /* Smoothstep: deterministic in Safari and close to the previous easing. */
    return t*t*(3-2*t);
  };

  const makeLogo=()=>{
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');
    svg.classList.add('pai-logo-motion');
    svg.setAttribute('viewBox','0 0 1990.6 1147.6');
    svg.setAttribute('fill','none');
    svg.setAttribute('aria-hidden','true');
    svg.setAttribute('focusable','false');

    const path=document.createElementNS(ns,'path');
    path.setAttribute('d',LOGO_PATH);
    path.setAttribute('fill','none');
    path.setAttribute('stroke','#000');
    path.setAttribute('stroke-width','43');
    path.setAttribute('stroke-linecap','round');
    path.setAttribute('stroke-linejoin','round');
    /* Keep the stroke hidden even before the first paint. */
    path.style.strokeDasharray='10000 10000';
    path.style.strokeDashoffset='10000';
    svg.appendChild(path);
    return {svg,path};
  };

  const startDraw=(host,path)=>{
    if(!path.isConnected) return;
    const length=path.getTotalLength();
    path.style.strokeDasharray=`${length} ${length}`;
    path.style.strokeDashoffset=String(length);

    /* Two frames guarantee Safari paints the hidden state before drawing. */
    requestAnimationFrame(()=>requestAnimationFrame(()=>{
      if(!path.isConnected) return;
      const started=performance.now();
      const duration=5000;
      const tick=now=>{
        if(!path.isConnected||!isHome()) return;
        const t=Math.min(1,(now-started)/duration);
        const p=ease(t);
        path.style.strokeDashoffset=String(length*(1-p));
        if(t<1){
          drawFrame=requestAnimationFrame(tick);
          return;
        }
        path.style.strokeDashoffset='0';
        drawFrame=0;
        exitTimer=window.setTimeout(()=>{
          if(!isHome()||!host.isConnected) return;
          host.classList.add('pai-logo-motion-exit');
          hideTimer=window.setTimeout(()=>host.classList.add('pai-logo-motion-hidden'),760);
        },450);
      };
      drawFrame=requestAnimationFrame(tick);
    }));
  };

  const init=(force=false)=>{
    scheduled=false;
    if(!isHome()) return;
    const host=document.querySelector('.home-hero .hero-art');
    if(!host) return;
    if(host.dataset.paiLogoMotion==='1'&&!force) return;

    clearMotion();
    host.dataset.paiLogoMotion='1';
    host.classList.add('pai-logo-motion-host');
    host.classList.remove('pai-logo-motion-exit','pai-logo-motion-hidden');

    const {svg,path}=makeLogo();
    host.replaceChildren(svg);

    if(matchMedia('(prefers-reduced-motion: reduce)').matches){
      path.style.strokeDasharray='none';
      path.style.strokeDashoffset='0';
      return;
    }
    startDraw(host,path);
  };

  const schedule=()=>{
    if(scheduled) return;
    scheduled=true;
    requestAnimationFrame(()=>init(false));
  };

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',schedule,{once:true});
  else schedule();

  /* SPA swaps can recreate the hero. */
  new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});
  addEventListener('popstate',schedule);

  /* iOS Safari can restore a fully rendered SVG on refresh/page restoration.
     Rebuild the SVG on every pageshow so the one-stroke starts from frame zero. */
  addEventListener('pageshow',()=>{
    if(!isHome()) return;
    requestAnimationFrame(()=>requestAnimationFrame(()=>init(true)));
  });
})();
