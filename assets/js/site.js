(function(){
  'use strict';

  const previewHost='tjpai.github.io';
  const isPreview=location.hostname===previewHost;
  const prefix=isPreview?'/pai-web':'';
  const root=p=>`${prefix}${p}`;
  const absolute=p=>new URL(root(p),location.origin).href;

  const normalizedPath=()=>{
    let p=location.pathname;
    if(prefix&&p.startsWith(prefix)) p=p.slice(prefix.length)||'/';
    if(p==='/index.html') p='/';
    if(p==='/en/index.html') p='/en/';
    return p;
  };

  const initialPath=normalizedPath();

  const installSharedStyles=()=>{
    if(document.getElementById('pai-shared-runtime-style')) return;
    const style=document.createElement('style');
    style.id='pai-shared-runtime-style';
    style.textContent=`
@media(max-width:768px){
  .research-grid .research .research-code{display:grid;grid-template-columns:auto auto minmax(0,1fr);align-items:center;column-gap:10px;row-gap:0;margin-bottom:22px;line-height:1}
  .research-grid .research .research-code-main{display:contents}
  .research-grid .research .research-index{font-size:16px!important;line-height:1.05!important;letter-spacing:.08em!important;font-weight:500!important;color:#A8AFB9!important;white-space:nowrap}
  .research-grid .research .research-code-main>span{font-size:17px;line-height:1.05;letter-spacing:.09em;font-weight:700;color:var(--ink);white-space:nowrap}
  .research-grid .research .research-expansion{font-size:9px;line-height:1.12;letter-spacing:.055em;font-weight:500;text-transform:uppercase;color:var(--muted);white-space:normal;text-wrap:balance;display:block;max-width:none}
  .research-grid .research:nth-child(1) .research-expansion{width:112px}
  .research-grid .research:nth-child(2) .research-expansion{width:146px}
  .research-grid .research:nth-child(3) .research-expansion{width:166px}
  .menu-btn{position:relative!important;width:50px!important;height:50px!important;padding:0!important;margin-right:-7px!important;font-size:0!important;line-height:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;outline:none!important;-webkit-appearance:none!important;appearance:none!important;-webkit-tap-highlight-color:transparent!important;color:#318AF5!important;touch-action:manipulation!important}
  .menu-btn:hover,.menu-btn:active,.menu-btn:focus,.menu-btn:focus-visible{background:transparent!important;box-shadow:none!important;outline:none!important}
  .menu-btn::before,.menu-btn::after{content:"";position:absolute;left:8px;width:34px;height:3px;border-radius:2px;background:currentColor;transform-origin:center;transition:top .18s ease,transform .18s ease,opacity .12s ease,box-shadow .18s ease;pointer-events:none}
  .menu-btn::before{top:13px;box-shadow:0 10px 0 currentColor,0 20px 0 currentColor}
  .menu-btn::after{top:23px;opacity:0}
  .menu-btn[aria-expanded="true"]::before{top:23px;box-shadow:none;transform:rotate(45deg)}
  .menu-btn[aria-expanded="true"]::after{top:23px;opacity:1;transform:rotate(-45deg)}
}
.pub-year-row{justify-content:flex-start!important;align-items:baseline!important;gap:12px!important}
.pub-year-row span{padding-bottom:0!important}
`;
    document.head.appendChild(style);
  };

  const ensureStylesheet=href=>new Promise(resolve=>{
    const target=new URL(href,location.href).href;
    const existing=[...document.querySelectorAll('link[rel="stylesheet"]')].find(link=>new URL(link.href,location.href).href===target);
    if(existing){ resolve(); return; }
    const link=document.createElement('link');
    link.rel='stylesheet';
    link.href=target;
    link.onload=()=>resolve();
    link.onerror=()=>resolve();
    document.head.appendChild(link);
    setTimeout(resolve,1200);
  });

  installSharedStyles();
  ensureStylesheet(absolute('/assets/css/team.css'));

  try{
    const saved=localStorage.getItem('pai-lang');
    const primary=(navigator.languages&&navigator.languages[0])||navigator.language||'en';
    const preferred=saved||(String(primary).toLowerCase().startsWith('zh')?'zh':'en');
    const isBot=/bot|crawler|spider|slurp/i.test(navigator.userAgent||'');
    if(!isBot&&initialPath==='/'&&preferred==='en'){
      location.replace(root('/en/'));
      return;
    }
  }catch(_e){}

  const languageMap={
    '/':'/en/',
    '/about.html':'/en/about.html',
    '/research.html':'/en/research.html',
    '/team.html':'/en/team.html',
    '/publications.html':'/en/publications.html',
    '/join.html':'/en/join.html',
    '/contact.html':'/en/contact.html',
    '/people/erwu-liu.html':'/en/people/erwu-liu.html',
    '/people/rui-wang.html':'/en/people/rui-wang.html',
    '/people/gang-shen.html':'/en/people/gang-shen.html',
    '/people/dunhui-xiao.html':'/en/people/dunhui-xiao.html',
    '/people/shuyan-hu.html':'/en/people/shuyan-hu.html',
    '/people/yan-liu.html':'/en/people/yan-liu.html'
  };
  const reverseLanguageMap=Object.fromEntries(Object.entries(languageMap).map(([zh,en])=>[en,zh]));

  const ensureLanguageLink=()=>{
    const p=normalizedPath();
    const isEn=p.startsWith('/en/');
    const counterpart=isEn?(reverseLanguageMap[p]||'/'):(languageMap[p]||'/en/');
    const label=isEn?'中文':'EN';
    for(const container of document.querySelectorAll('.nav-links,.mobile-menu')){
      const existing=[...container.querySelectorAll('a')].find(a=>/^(EN|中文)$/.test((a.textContent||'').trim()));
      if(existing){ existing.href=root(counterpart); existing.textContent=label; }
      else{
        const a=document.createElement('a');
        a.href=root(counterpart);
        a.textContent=label;
        container.appendChild(a);
      }
    }
  };

  const ensureMobileMenu=()=>{
    const header=document.querySelector('.site-header');
    const desktop=header?.querySelector('.nav-links');
    if(!header||!desktop||header.querySelector('.mobile-menu')) return;
    const mobile=document.createElement('nav');
    mobile.className='mobile-menu';
    mobile.innerHTML=desktop.innerHTML;
    header.appendChild(mobile);
  };

  const prepareMenuButton=()=>{
    ensureMobileMenu();
    const btn=document.querySelector('.menu-btn');
    if(btn) btn.setAttribute('aria-expanded','false');
  };

  const normalizeCopy=()=>{
    if((document.documentElement.lang||'').toLowerCase().startsWith('zh')){
      for(const h2 of document.querySelectorAll('h2')){
        if((h2.textContent||'').trim()==='高水平科研与代表成果') h2.textContent='代表性成果';
      }
    }
  };

  const initializeChrome=()=>{
    ensureLanguageLink();
    prepareMenuButton();
    normalizeCopy();
  };
  initializeChrome();

  /* One delegated menu handler for the lifetime of the document. Header swaps do not require rebinding. */
  document.addEventListener('click',event=>{
    const btn=event.target.closest&&event.target.closest('.menu-btn');
    if(!btn) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    ensureMobileMenu();
    const menu=document.querySelector('.site-header .mobile-menu');
    if(!menu) return;
    const open=menu.classList.toggle('open');
    btn.setAttribute('aria-expanded',open?'true':'false');
  },true);

  document.addEventListener('click',event=>{
    const a=event.target.closest&&event.target.closest('a');
    if(!a) return;
    const label=(a.textContent||'').trim();
    try{
      if(label==='EN') localStorage.setItem('pai-lang','en');
      else if(label==='中文') localStorage.setItem('pai-lang','zh');
    }catch(_e){}
  });

  const addHead=(tag,attrs)=>{
    const el=document.createElement(tag);
    Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));
    document.head.appendChild(el);
    return el;
  };

  const updateMetadata=(doc,target)=>{
    document.title=doc.title||document.title;
    const nextDescription=doc.querySelector('meta[name="description"]')?.content;
    let description=document.querySelector('meta[name="description"]');
    if(nextDescription){
      if(!description) description=addHead('meta',{name:'description',content:nextDescription});
      else description.content=nextDescription;
    }
    let canonical=document.querySelector('link[rel="canonical"]');
    if(!canonical) canonical=addHead('link',{rel:'canonical',href:target.href});
    canonical.href=target.href.split('#')[0];
  };

  let siteCacheReady=Promise.resolve();
  if('serviceWorker' in navigator){
    siteCacheReady=(async()=>{
      try{
        const registration=await navigator.serviceWorker.register(root('/sw.js'),{updateViaCache:'none'});
        await navigator.serviceWorker.ready;
        if(registration.waiting) registration.waiting.postMessage({type:'SKIP_WAITING'});
      }catch(_e){}
    })();
  }

  const cacheVersion=name=>{
    const m=String(name).match(/-(\d+)$/);
    return m?Number(m[1]):0;
  };

  const cacheNames=async()=>{
    if(!('caches' in window)) return [];
    return (await caches.keys())
      .filter(name=>name.startsWith('pai-site-'))
      .sort((a,b)=>cacheVersion(b)-cacheVersion(a));
  };

  const cachedResponse=async url=>{
    if(!('caches' in window)) return null;
    for(const name of await cacheNames()){
      const cache=await caches.open(name);
      let hit=await cache.match(url.href,{ignoreSearch:true});
      if(hit) return hit;
      if(url.pathname.endsWith('/')){
        const indexUrl=new URL(url.href);
        indexUrl.pathname=url.pathname+'index.html';
        hit=await cache.match(indexUrl.href,{ignoreSearch:true});
        if(hit) return hit;
      }
    }
    return null;
  };

  const responseFor=async url=>{
    const cached=await cachedResponse(url);
    if(cached) return cached;
    try{
      const response=await fetch(url.href,{cache:'force-cache',credentials:'same-origin'});
      return response&&response.ok?response:null;
    }catch(_e){ return null; }
  };

  let publicationDataPromise=null;
  const jsonFor=async path=>{
    const response=await responseFor(new URL(absolute(path)));
    if(!response||!response.ok) throw new Error('resource unavailable');
    return response.json();
  };
  const getPublicationData=()=>{
    if(!publicationDataPromise){
      publicationDataPromise=Promise.all([
        jsonFor('/data/publications.json'),
        jsonFor('/data/publications-archive.json').catch(()=>[])
      ]).then(parts=>parts.flat().sort((a,b)=>b.year-a.year));
    }
    return publicationDataPromise;
  };
  getPublicationData().catch(()=>{});

  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'}[m]));
  const doiHref=doi=>'https://doi.org/'+String(doi).trim().split('/').map(encodeURIComponent).join('/');

  const initPublications=async()=>{
    const host=document.querySelector('[data-publications]');
    if(!host) return;
    try{
      const items=await getPublicationData();
      const byYear=new Map();
      items.forEach(item=>{
        if(!byYear.has(item.year)) byYear.set(item.year,[]);
        byYear.get(item.year).push(item);
      });
      const fragment=document.createDocumentFragment();
      for(const [year,pubs] of byYear){
        const section=document.createElement('section');
        section.className='pub-group';
        const count=`${pubs.length} publication${pubs.length===1?'':'s'}`;
        section.innerHTML=`<div class="pub-year-row"><h2 class="pub-year">${year}</h2><span>${count}</span></div>`;
        pubs.forEach(p=>{
          const article=document.createElement('article');
          article.className='pub';
          const actions=p.doi?`<div class="pub-actions"><a href="${esc(doiHref(p.doi))}" target="_blank" rel="noopener">DOI ↗</a></div>`:'';
          article.innerHTML=`<h3>${esc(p.title)}</h3><p class="pub-authors">${esc(p.authors)}</p><p class="pub-venue">${esc(p.venue)} · ${year}</p>${actions}`;
          section.appendChild(article);
        });
        fragment.appendChild(section);
      }
      host.replaceChildren(fragment);
      host.dataset.paiInitialized='1';
    }catch(_e){
      const en=(document.documentElement.lang||'').toLowerCase().startsWith('en');
      host.innerHTML=`<p class="muted">${en?'Publications are temporarily unavailable. Please refresh later.':'论文数据暂时无法载入，请稍后刷新。'}</p>`;
    }
  };
  initPublications();

  const syncHeadStyles=async(doc,targetUrl)=>{
    const waits=[];
    for(const link of doc.querySelectorAll('head link[rel="stylesheet"]')){
      const raw=link.getAttribute('href');
      if(raw) waits.push(ensureStylesheet(new URL(raw,targetUrl).href));
    }
    document.querySelectorAll('style[data-pai-page-head]').forEach(el=>el.remove());
    for(const source of doc.querySelectorAll('head > style')){
      const copy=document.createElement('style');
      copy.dataset.paiPageHead='1';
      copy.textContent=source.textContent||'';
      document.head.appendChild(copy);
    }
    await Promise.all(waits);
  };

  try{ history.scrollRestoration='manual'; }catch(_e){}
  let transitioning=false;
  let scrollTick=0;

  const saveScroll=(force=false)=>{
    if(transitioning&&!force) return;
    try{
      history.replaceState(Object.assign({},history.state||{},{paiRoute:true,scrollX:window.scrollX,scrollY:window.scrollY}),'',location.href);
    }catch(_e){}
  };

  if(!history.state||history.state.paiRoute!==true){
    try{ history.replaceState({paiRoute:true,scrollX:window.scrollX,scrollY:window.scrollY},'',location.href); }catch(_e){}
  }

  window.addEventListener('scroll',()=>{
    if(transitioning||scrollTick) return;
    scrollTick=requestAnimationFrame(()=>{
      scrollTick=0;
      saveScroll();
    });
  },{passive:true});
  window.addEventListener('pagehide',()=>saveScroll(true));

  const restorePosition=(target,state)=>new Promise(resolve=>{
    const apply=()=>{
      if(state&&Number.isFinite(state.scrollY)){
        window.scrollTo(Number.isFinite(state.scrollX)?state.scrollX:0,state.scrollY);
      }else if(target.hash){
        const id=decodeURIComponent(target.hash.slice(1));
        const element=document.getElementById(id);
        if(element) element.scrollIntoView();
        else window.scrollTo(0,0);
      }else{
        window.scrollTo(0,0);
      }
    };
    requestAnimationFrame(()=>requestAnimationFrame(()=>{
      apply();
      setTimeout(()=>{ apply(); resolve(); },100);
    }));
  });

  const renderPage=async(target,{push=true,restoreState=null}={})=>{
    const requestUrl=new URL(target.href);
    requestUrl.hash='';
    const response=await responseFor(requestUrl);
    if(!response) return false;
    const doc=new DOMParser().parseFromString(await response.text(),'text/html');
    const nextHeader=doc.querySelector('.site-header');
    const nextMain=doc.querySelector('main');
    const nextFooter=doc.querySelector('.site-footer');
    const currentHeader=document.querySelector('.site-header');
    const currentMain=document.querySelector('main');
    const currentFooter=document.querySelector('.site-footer');
    if(!nextHeader||!nextMain||!nextFooter||!currentHeader||!currentMain||!currentFooter) return false;

    await syncHeadStyles(doc,requestUrl);
    currentHeader.replaceWith(document.importNode(nextHeader,true));
    currentMain.replaceWith(document.importNode(nextMain,true));
    currentFooter.replaceWith(document.importNode(nextFooter,true));
    document.documentElement.lang=doc.documentElement.lang||document.documentElement.lang;
    document.body.className=doc.body.className||'';
    updateMetadata(doc,target);

    if(push) history.pushState({paiRoute:true,scrollX:0,scrollY:0},'',target.pathname+target.search+target.hash);

    initializeChrome();
    await initPublications();
    await restorePosition(target,restoreState);
    return true;
  };

  const isRouteableInternal=a=>{
    if(!a||a.target==='_blank'||a.hasAttribute('download')) return false;
    const raw=a.getAttribute('href')||'';
    if(!raw||raw.startsWith('mailto:')||raw.startsWith('tel:')||raw.startsWith('javascript:')) return false;
    const target=new URL(a.href,location.href);
    if(target.origin!==location.origin) return false;
    if(prefix&&!target.pathname.startsWith(prefix)) return false;
    return target.pathname.endsWith('/')||target.pathname.endsWith('.html');
  };

  document.addEventListener('click',async event=>{
    if(event.defaultPrevented||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    if(typeof event.button==='number'&&event.button!==0) return;
    const a=event.target.closest&&event.target.closest('a');
    if(!isRouteableInternal(a)) return;

    const target=new URL(a.href,location.href);
    event.preventDefault();
    event.stopImmediatePropagation();

    const currentNoHash=location.origin+location.pathname+location.search;
    const targetNoHash=target.origin+target.pathname+target.search;

    if(currentNoHash===targetNoHash){
      const menu=document.querySelector('.mobile-menu');
      const btn=document.querySelector('.menu-btn');
      menu?.classList.remove('open');
      btn?.setAttribute('aria-expanded','false');
      if(target.hash&&target.hash!==location.hash){
        saveScroll(true);
        history.pushState({paiRoute:true,scrollX:0,scrollY:0},'',target.pathname+target.search+target.hash);
        transitioning=true;
        await restorePosition(target,null);
        transitioning=false;
        saveScroll(true);
      }else if(!target.hash){
        window.scrollTo(0,0);
        saveScroll(true);
      }
      return;
    }

    saveScroll(true);
    transitioning=true;
    try{
      const ok=await renderPage(target,{push:true,restoreState:null});
      if(!ok) throw new Error('route failed');
    }catch(_e){}
    finally{
      transitioning=false;
      saveScroll(true);
    }
  },true);

  window.addEventListener('popstate',async event=>{
    transitioning=true;
    try{
      await renderPage(new URL(location.href),{push:false,restoreState:event.state||null});
    }catch(_e){}
    finally{
      transitioning=false;
      saveScroll(true);
    }
  });

  siteCacheReady.catch(()=>{});
})();
