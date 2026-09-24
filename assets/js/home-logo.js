(function(){
  'use strict';

  const HOME_PATHS=new Set(['/','/index.html','/en/','/en/index.html']);
  const LOGO_PATH='M 93.8,88.8 L 597.8,88.9 L 632.9,91.0 L 666.3,97.3 L 697.8,108.2 L 727.2,124.0 L 750.1,141.1 L 775.3,166.1 L 792.4,189.0 L 808.3,218.4 L 817.7,244.6 L 823.5,272.1 L 825.5,307.1 L 822.2,341.7 L 813.6,374.2 L 800.0,404.5 L 781.5,432.8 L 757.5,458.6 L 730.5,480.3 L 701.1,496.4 L 659.1,510.9 L 607.7,517.1 L 266.0,517.8 L 225.1,520.4 L 197.8,527.0 L 167.7,541.3 L 140.6,562.5 L 121.6,584.4 L 109.8,603.5 L 98.8,629.0 L 93.1,650.6 L 89.7,679.2 L 90.0,900.3 L 92.1,929.5 L 96.3,951.7 L 103.5,972.7 L 114.6,992.1 L 129.4,1010.0 L 146.8,1025.4 L 165.8,1037.4 L 186.1,1046.4 L 213.2,1053.3 L 236.2,1055.2 L 270.4,1051.6 L 302.8,1042.7 L 333.1,1029.0 L 356.4,1012.8 L 899.6,453.2 L 917.7,439.4 L 942.6,427.1 L 969.6,419.7 L 998.1,416.6 L 1026.8,418.7 L 1059.3,427.1 L 1084.1,439.6 L 1102.3,453.7 L 1611.0,980.8 L 1649.8,1016.9 L 1673.7,1031.7 L 1699.2,1042.6 L 1726.1,1050.1 L 1748.8,1053.3 L 1766.0,1053.8 L 1788.5,1050.8 L 1809.9,1044.5 L 1829.8,1034.7 L 1857.1,1013.9 L 1878.8,987.1 L 1892.3,956.7 L 1898.3,923.2 L 1899.8,881.8 L 1899.8,89.8';
  const MINING_SOURCE='https://epaper.gmw.cn/gmrb/html/2014-04/27/nw.D110000gmrb_20140427_4-04.htm';
  const CHINA_DAILY_SOURCE='https://www.chinadaily.com.cn/a/201811/05/WS5bdf8c2da310eff303286767.html';

  let frame=0;
  let exitTimer=0;
  let hideTimer=0;
  let scheduled=false;

  const normalizedPath=()=>{
    let path=location.pathname||'/';
    if(location.hostname==='tjpai.github.io'&&path.startsWith('/pai-web')) path=path.slice('/pai-web'.length)||'/';
    return path;
  };
  const isHome=()=>HOME_PATHS.has(normalizedPath());
  const ease=t=>t*t*(3-2*t);

  const syncHomepageEditorialLinks=()=>{
    if(!isHome()) return;

    const image=document.querySelector('img[src$="datong-mine-magnetic-communication.webp"]');
    const link=image?.closest('a');
    const caption=link?.querySelector('figcaption');
    if(link&&caption){
      link.href=MINING_SOURCE;
      const isEnglish=document.documentElement.lang.toLowerCase().startsWith('en');
      caption.innerHTML=isEnglish
        ? '<strong>Mining · Through-the-Earth Magnetic Communication</strong>Guangming Daily feature on Tongji University’s deep-penetration wireless communication rescue equipment.<span class="impact-visual-source">Guangming Daily</span>'
        : '<strong>煤矿 · 跨介质磁通信</strong>《接通“地心来电”》：同济大学教授研发国内最大穿透深度无线通信救援设备。<span class="impact-visual-source">光明日报</span>';
    }

    /* Homepage media selection: keep the Tongji 2023 Guide-system story and
       remove the overlapping 2018 China News Service positioning story. */
    const mediaItems=[...document.querySelectorAll('.media-coverage .media-list .media-item')];
    mediaItems.forEach(item=>{
      const meta=(item.querySelector('.media-meta')?.textContent||'').trim();
      if(/中国新闻网\s*·\s*2018|China News Service\s*·\s*2018/i.test(meta)) item.remove();
      if(/China Daily\s*·\s*2018/i.test(meta)) item.href=CHINA_DAILY_SOURCE;
    });
  };

  const stop=()=>{
    if(frame) cancelAnimationFrame(frame);
    if(exitTimer) clearTimeout(exitTimer);
    if(hideTimer) clearTimeout(hideTimer);
    frame=exitTimer=hideTimer=0;
  };

  const makeLogo=()=>{
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');
    svg.classList.add('pai-logo-motion');
    svg.setAttribute('viewBox','0 0 1990.6 1147.6');
    svg.setAttribute('fill','none');
    svg.setAttribute('aria-hidden','true');

    const path=document.createElementNS(ns,'path');
    path.setAttribute('d',LOGO_PATH);
    path.setAttribute('fill','none');
    path.setAttribute('stroke','#000');
    path.setAttribute('stroke-width','43');
    path.setAttribute('stroke-linecap','round');
    path.setAttribute('stroke-linejoin','round');
    path.style.opacity='0';
    svg.appendChild(path);
    return {svg,path};
  };

  const draw=(host,path)=>{
    const length=path.getTotalLength();
    const start=Math.max(0,length-.75); /* avoids Safari flashing the final round cap */
    path.style.strokeDasharray=`${length} ${length}`;
    path.style.strokeDashoffset=String(start);

    requestAnimationFrame(()=>requestAnimationFrame(()=>{
      if(!path.isConnected||!isHome()) return;
      path.style.opacity='1';
      host.classList.add('pai-logo-motion-ready');
      const started=performance.now();

      const tick=now=>{
        if(!path.isConnected||!isHome()) return;
        const t=Math.min(1,(now-started)/5000);
        path.style.strokeDashoffset=String(start*(1-ease(t)));
        if(t<1){frame=requestAnimationFrame(tick);return;}

        frame=0;
        path.style.strokeDashoffset='0';
        exitTimer=setTimeout(()=>{
          if(!host.isConnected||!isHome()) return;
          host.classList.add('pai-logo-motion-exit');
          hideTimer=setTimeout(()=>host.classList.add('pai-logo-motion-hidden'),720);
        },450);
      };
      frame=requestAnimationFrame(tick);
    }));
  };

  const initHomeLogo=(force=false)=>{
    scheduled=false;
    if(!isHome()) return;
    syncHomepageEditorialLinks();
    const host=document.querySelector('.home-hero .hero-art');
    if(!host||(!force&&host.dataset.paiLogoMotion==='1')) return;

    stop();
    host.dataset.paiLogoMotion='1';
    host.classList.add('pai-logo-motion-host');
    host.classList.remove('pai-logo-motion-ready','pai-logo-motion-exit','pai-logo-motion-hidden');

    const {svg,path}=makeLogo();
    host.replaceChildren(svg);

    if(matchMedia('(prefers-reduced-motion: reduce)').matches){
      path.style.opacity='1';
      host.classList.add('pai-logo-motion-ready');
      return;
    }
    draw(host,path);
  };

  const schedule=()=>{
    if(scheduled) return;
    scheduled=true;
    requestAnimationFrame(()=>initHomeLogo(false));
  };

  window.initHomeLogo=initHomeLogo;

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',schedule,{once:true});
  else schedule();

  /* Needed only because the site swaps <main> without a full page load. */
  new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});
  addEventListener('pageshow',event=>{if(event.persisted) initHomeLogo(true);});
})();
