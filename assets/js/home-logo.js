(function(){
  'use strict';

  const HOME_PATHS=new Set(['/','/index.html','/en/','/en/index.html']);
  const LOGO_PATH='M 93.8,88.8 L 597.8,88.9 L 632.9,91.0 L 666.3,97.3 L 697.8,108.2 L 727.2,124.0 L 750.1,141.1 L 775.3,166.1 L 792.4,189.0 L 808.3,218.4 L 817.7,244.6 L 823.5,272.1 L 825.5,307.1 L 822.2,341.7 L 813.6,374.2 L 800.0,404.5 L 781.5,432.8 L 757.5,458.6 L 730.5,480.3 L 701.1,496.4 L 659.1,510.9 L 607.7,517.1 L 266.0,517.8 L 225.1,520.4 L 197.8,527.0 L 167.7,541.3 L 140.6,562.5 L 121.6,584.4 L 109.8,603.5 L 98.8,629.0 L 93.1,650.6 L 89.7,679.2 L 90.0,900.3 L 92.1,929.5 L 96.3,951.7 L 103.5,972.7 L 114.6,992.1 L 129.4,1010.0 L 146.8,1025.4 L 165.8,1037.4 L 186.1,1046.4 L 213.2,1053.3 L 236.2,1055.2 L 270.4,1051.6 L 302.8,1042.7 L 333.1,1029.0 L 356.4,1012.8 L 899.6,453.2 L 917.7,439.4 L 942.6,427.1 L 969.6,419.7 L 998.1,416.6 L 1026.8,418.7 L 1059.3,427.1 L 1084.1,439.6 L 1102.3,453.7 L 1611.0,980.8 L 1649.8,1016.9 L 1673.7,1031.7 L 1699.2,1042.6 L 1726.1,1050.1 L 1748.8,1053.3 L 1766.0,1053.8 L 1788.5,1050.8 L 1809.9,1044.5 L 1829.8,1034.7 L 1857.1,1013.9 L 1878.8,987.1 L 1892.3,956.7 L 1898.3,923.2 L 1899.8,881.8 L 1899.8,89.8';
  const MINING_SOURCE='https://epaper.gmw.cn/gmrb/html/2014-04/27/nw.D110000gmrb_20140427_4-04.htm';
  const CHINA_DAILY_SOURCE='https://www.chinadaily.com.cn/a/201811/05/WS5bdf8c2da310eff303286767.html';
  const CIIE_SOURCE='https://tv.cctv.com/2019/11/08/VIDEWMSICpz1YFdyGCUAeHR4191108.shtml';
  const MICROSOFT_SOURCE='https://www.chinanews.com/m/gn/2018/04-19/8494909.shtml';

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

  const reshapeHomepage=()=>{
    if(!isHome()||document.querySelector('.home-achievement-stories')) return;
    const isEnglish=document.documentElement.lang.toLowerCase().startsWith('en');
    const sections=[...document.querySelectorAll('main > section')];
    const findSection=label=>sections.find(section=>(section.querySelector('.section-head .eyebrow')?.textContent||'').trim().toLowerCase()===label.toLowerCase());
    const achievementSection=findSection('Research Excellence');
    const impactSection=findSection('Impact & Translation');
    const join=document.querySelector('main > .join');
    if(!achievementSection||!join) return;

    const container=achievementSection.querySelector('.container');
    const head=container?.querySelector('.section-head');
    const media=container?.querySelector('.media-coverage');
    if(!container||!head||!media) return;

    [...media.querySelectorAll('.media-item')].forEach(item=>{
      const meta=(item.querySelector('.media-meta')?.textContent||'').trim();
      const title=(item.querySelector('.media-title')?.textContent||'').trim();
      if(/中国新闻网\s*·\s*2018|China News Service\s*·\s*2018/i.test(meta)) item.remove();
      if(/光明日报\s*·\s*2014|Guangming Daily\s*·\s*2014/i.test(meta)&&/上海科学家|Shanghai scientists/i.test(title)) item.remove();
      if(/China Daily\s*·\s*2018/i.test(meta)) item.href=CHINA_DAILY_SOURCE;
    });

    const prefix=isEnglish?'../':'';
    const stories=document.createElement('div');
    stories.className='home-achievement-stories';
    stories.innerHTML=isEnglish?`
      <figure class="home-achievement-story"><a href="${MICROSOFT_SOURCE}" target="_blank" rel="noopener noreferrer"><img src="${prefix}assets/images/home/microsoft-indoor-localization-competition.webp" alt="PAI team at the Microsoft Indoor Localization Competition" loading="lazy" decoding="async"><figcaption><strong>Microsoft Indoor Localization Competition</strong><span>Champion, 2016 · Runner-up, 2018</span><small>China News Service</small></figcaption></a></figure>
      <figure class="home-achievement-story"><a href="${CIIE_SOURCE}" target="_blank" rel="noopener noreferrer"><img src="${prefix}assets/images/home/ciie-navigation.webp" alt="Smart navigation at the China International Import Expo" loading="lazy" decoding="async"><figcaption><strong>CIIE · High-Precision Localization & Smart Navigation</strong><span>The “Guide” system served the China International Import Expo for six consecutive years.</span><small>CCTV News</small></figcaption></a></figure>
      <figure class="home-achievement-story"><a href="${MINING_SOURCE}" target="_blank" rel="noopener noreferrer"><img src="${prefix}assets/images/home/datong-mine-magnetic-communication.webp" alt="Through-the-earth magnetic communication rescue equipment" loading="lazy" decoding="async"><figcaption><strong>Through-the-Earth Magnetic Communication</strong><span>Deep-penetration wireless rescue communication for underground and mining environments.</span><small>Guangming Daily</small></figcaption></a></figure>`:`
      <figure class="home-achievement-story"><a href="${MICROSOFT_SOURCE}" target="_blank" rel="noopener noreferrer"><img src="${prefix}assets/images/home/microsoft-indoor-localization-competition.webp" alt="PAI团队参加微软全球室内定位技术大赛" loading="lazy" decoding="async"><figcaption><strong>微软全球室内定位技术大赛</strong><span>2016 年冠军 · 2018 年亚军</span><small>中国新闻网</small></figcaption></a></figure>
      <figure class="home-achievement-story"><a href="${CIIE_SOURCE}" target="_blank" rel="noopener noreferrer"><img src="${prefix}assets/images/home/ciie-navigation.webp" alt="进博会高精定位与智能导览应用" loading="lazy" decoding="async"><figcaption><strong>进博会 · 高精定位与智能导览</strong><span>“导路者”系统连续 6 年服务中国国际进口博览会。</span><small>央视新闻</small></figcaption></a></figure>
      <figure class="home-achievement-story"><a href="${MINING_SOURCE}" target="_blank" rel="noopener noreferrer"><img src="${prefix}assets/images/home/datong-mine-magnetic-communication.webp" alt="深穿透磁通信救援设备工程应用" loading="lazy" decoding="async"><figcaption><strong>深穿透磁通信</strong><span>面向地下、煤矿等复杂环境的深穿透无线通信救援设备。</span><small>光明日报</small></figcaption></a></figure>`;

    [...container.children].forEach(child=>{if(child!==head) child.remove();});
    container.appendChild(stories);
    const more=document.createElement('div');
    more.className='home-achievements-more';
    more.innerHTML=`<a class="text-link" href="publications.html">${isEnglish?'More research results →':'更多研究成果 →'}</a>`;
    container.appendChild(more);

    const platformSection=document.getElementById('selected-updates');
    if(platformSection){
      const platformContainer=platformSection.querySelector('.container');
      if(platformContainer){
        platformContainer.innerHTML=isEnglish?`
          <div class="section-head"><div class="eyebrow">COLLABORATION PLATFORMS</div><h2 class="title-section">Collaboration Platforms</h2></div>
          <div class="updates-grid">
            <article class="update-item"><div class="update-meta">JOURNAL</div><h3 class="title-item">IET Blockchain</h3><p>Founding Editor-in-Chief institution for an open-access international blockchain journal.</p></article>
            <article class="update-item"><div class="update-meta">CONFERENCE</div><h3 class="title-item">IEEE Global Blockchain Conference</h3><p>Conference chair institution connecting frontier research, industry and global collaboration.</p></article>
            <article class="update-item"><div class="update-meta">TECHNICAL COMMUNITY</div><h3 class="title-item">IEEE Blockchain Technical Community (BCTC)</h3><p>China leadership institution supporting technical-community development across China and Asia-Pacific.</p></article>
          </div>
          <div class="home-platform-more"><a class="text-link" href="about.html#international-impact">Platforms & impact →</a></div>`:`
          <div class="section-head"><div class="eyebrow">COLLABORATION PLATFORMS</div><h2 class="title-section">合作平台</h2></div>
          <div class="updates-grid">
            <article class="update-item"><div class="update-meta">期刊</div><h3 class="title-item">IET Blockchain</h3><p>创刊主编单位，建设开放获取的国际区块链学术期刊平台。</p></article>
            <article class="update-item"><div class="update-meta">会议</div><h3 class="title-item">IEEE Global Blockchain Conference</h3><p>大会主席单位，连接前沿研究、产业协同与国际合作。</p></article>
            <article class="update-item"><div class="update-meta">技术社区</div><h3 class="title-item">IEEE Blockchain Technical Community (BCTC)</h3><p>中国区主席单位，推动中国及亚太区技术社区建设。</p></article>
          </div>
          <div class="home-platform-more"><a class="text-link" href="about.html#international-impact">了解平台及影响力 →</a></div>`;
      }
    }

    const mediaSection=document.createElement('section');
    mediaSection.className='section home-media-section';
    mediaSection.innerHTML=`<div class="container"><div class="section-head"><div class="eyebrow">MEDIA COVERAGE</div><h2 class="title-section">${isEnglish?'Media Coverage':'媒体报道'}</h2></div></div>`;
    media.classList.add('home-media-coverage');
    mediaSection.querySelector('.container').appendChild(media);
    join.before(mediaSection);

    if(impactSection) impactSection.remove();
  };

  const syncHomepageEditorialLinks=()=>{ if(isHome()) reshapeHomepage(); };

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
    const start=Math.max(0,length-.75);
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
  new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});
  addEventListener('pageshow',event=>{if(event.persisted) initHomeLogo(true);});
})();
