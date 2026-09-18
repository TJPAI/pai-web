(function(){
  const previewHost='tjpai.github.io';
  const isPreview=location.hostname===previewHost;
  const prefix=isPreview?'/pai-web':'';
  const base=location.origin+prefix;
  const root=p=>`${prefix}${p}`;
  let siteCacheReady=Promise.resolve();

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
  .menu-btn{position:relative!important;width:50px!important;height:50px!important;padding:0!important;margin-right:-7px!important;font-size:0!important;line-height:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;outline:none!important;-webkit-appearance:none!important;appearance:none!important;-webkit-tap-highlight-color:transparent!important;color:#318AF5!important}
  .menu-btn:hover,.menu-btn:active,.menu-btn:focus,.menu-btn:focus-visible{background:transparent!important;box-shadow:none!important;outline:none!important}
  .menu-btn::before,.menu-btn::after{content:"";position:absolute;left:8px;width:34px;height:3px;border-radius:2px;background:currentColor;transform-origin:center;transition:top .18s ease,transform .18s ease,opacity .12s ease,box-shadow .18s ease}
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
  installSharedStyles();

  const normalizedPath=()=>{
    let p=location.pathname;
    if(prefix&&p.startsWith(prefix)) p=p.slice(prefix.length)||'/';
    if(p==='/index.html') p='/';
    if(p==='/en/index.html') p='/en/';
    return p;
  };

  const initialPath=normalizedPath();

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

  const map={
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
  const reverse=Object.fromEntries(Object.entries(map).map(([zh,en])=>[en,zh]));

  const bindMenuToggle=()=>{
    const menuBtn=document.querySelector('.menu-btn');
    const mobileMenu=document.querySelector('.mobile-menu');
    if(!menuBtn||!mobileMenu||menuBtn.dataset.bound==='1') return;
    menuBtn.dataset.bound='1';
    menuBtn.setAttribute('aria-expanded','false');
    menuBtn.addEventListener('click',()=>{
      const open=mobileMenu.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded',open?'true':'false');
    });
  };

  const ensureLanguageLink=()=>{
    const p=normalizedPath();
    const isEn=p.startsWith('/en/');
    const counterpartPath=isEn?(reverse[p]||'/'):(map[p]||'/en/');
    const label=isEn?'中文':'EN';
    for(const container of document.querySelectorAll('.nav-links,.mobile-menu')){
      const existing=[...container.querySelectorAll('a')].find(a=>/^(EN|中文)$/.test((a.textContent||'').trim()));
      if(existing){ existing.href=root(counterpartPath); existing.textContent=label; }
      else{
        const a=document.createElement('a');
        a.href=root(counterpartPath); a.textContent=label; container.appendChild(a);
      }
    }
  };

  const normalizeCopy=()=>{
    if((document.documentElement.lang||'').toLowerCase().startsWith('zh')){
      for(const h2 of document.querySelectorAll('h2')){
        if((h2.textContent||'').trim()==='高水平科研与代表成果') h2.textContent='代表性成果';
      }
    }
  };

  bindMenuToggle();
  ensureLanguageLink();
  normalizeCopy();

  document.addEventListener('click',event=>{
    const a=event.target.closest&&event.target.closest('a');
    if(!a) return;
    const label=(a.textContent||'').trim();
    try{
      if(label==='EN') localStorage.setItem('pai-lang','en');
      else if(label==='中文') localStorage.setItem('pai-lang','zh');
    }catch(_e){}
  });

  const addHead=(tag,attrs)=>{const el=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));document.head.appendChild(el);return el;};
  const canonical=base+initialPath;
  if(!document.querySelector('link[rel="canonical"]')) addHead('link',{rel:'canonical',href:canonical});
  const title=document.title||'PAI Research Center';
  const description=document.querySelector('meta[name="description"]')?.content||'PAI Research Center at Tongji University.';
  const meta=(property,content)=>{if(!document.querySelector(`meta[property="${property}"]`)) addHead('meta',{property,content});};
  meta('og:type','website'); meta('og:title',title); meta('og:description',description); meta('og:url',canonical); meta('og:site_name','PAI Research Center · Tongji University');

  if('serviceWorker' in navigator){
    siteCacheReady=(async()=>{
      try{
        const registration=await navigator.serviceWorker.register(root('/sw.js'),{updateViaCache:'none'});
        await navigator.serviceWorker.ready;
        if(registration.waiting) registration.waiting.postMessage({type:'SKIP_WAITING'});
        sessionStorage.setItem('pai-sw-checked','1');
      }catch(_e){}
    })();
  }

  const cacheVersion=name=>{
    const m=String(name).match(/-(\d+)$/);
    return m?Number(m[1]):0;
  };

  const responseFor=async url=>{
    await siteCacheReady;
    if('caches' in window){
      const names=(await caches.keys())
        .filter(name=>name.startsWith('pai-site-'))
        .sort((a,b)=>cacheVersion(b)-cacheVersion(a));
      for(const name of names){
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
    }
    try{
      const r=await fetch(url.href,{cache:'force-cache',credentials:'same-origin'});
      return r&&r.ok?r:null;
    }catch(_e){ return null; }
  };

  const jsonFor=async path=>{
    const response=await responseFor(new URL(root(path),location.origin));
    if(!response||!response.ok) throw new Error('resource unavailable');
    return response.json();
  };

  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const doiHref=doi=>'https://doi.org/'+String(doi).trim().split('/').map(encodeURIComponent).join('/');

  const initPublications=async()=>{
    const host=document.querySelector('[data-publications]');
    if(!host||host.dataset.paiInitialized==='1') return;
    host.dataset.paiInitialized='1';
    host.innerHTML='';
    const en=(document.documentElement.lang||'').toLowerCase().startsWith('en');
    try{
      const [recent,archive]=await Promise.all([
        jsonFor('/data/publications.json'),
        jsonFor('/data/publications-archive.json').catch(()=>[])
      ]);
      const items=[...recent,...archive].sort((a,b)=>b.year-a.year);
      const byYear=new Map();
      items.forEach(item=>{
        if(!byYear.has(item.year)) byYear.set(item.year,[]);
        byYear.get(item.year).push(item);
      });
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
        host.appendChild(section);
      }
    }catch(_e){
      host.innerHTML=`<p class="muted">${en?'Publications are temporarily unavailable. Please refresh later.':'论文数据暂时无法载入，请稍后刷新。'}</p>`;
    }
  };

  try{ history.scrollRestoration='manual'; }catch(_e){}

  const saveScroll=()=>{
    try{
      history.replaceState(Object.assign({},history.state||{},{paiRoute:true,scrollX:window.scrollX,scrollY:window.scrollY}),'',location.href);
    }catch(_e){}
  };

  if(!history.state||history.state.paiRoute!==true){
    try{ history.replaceState({paiRoute:true,scrollX:window.scrollX,scrollY:window.scrollY},'',location.href); }catch(_e){}
  }

  let scrollTick=0;
  window.addEventListener('scroll',()=>{
    if(scrollTick) return;
    scrollTick=requestAnimationFrame(()=>{scrollTick=0;saveScroll();});
  },{passive:true});
  window.addEventListener('pagehide',saveScroll);

  const settleScroll=(target,restore)=>{
    const apply=()=>{
      if(restore&&Number.isFinite(restore.scrollY)){
        window.scrollTo(Number.isFinite(restore.scrollX)?restore.scrollX:0,restore.scrollY);
      }else if(target.hash){
        const id=decodeURIComponent(target.hash.slice(1));
        document.getElementById(id)?.scrollIntoView();
      }else{
        window.scrollTo(0,0);
      }
      saveScroll();
    };
    requestAnimationFrame(()=>requestAnimationFrame(apply));
    setTimeout(apply,80);
  };

  const renderPage=async(target,push=true,restore=null)=>{
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

    if(push) saveScroll();
    currentHeader.replaceWith(document.importNode(nextHeader,true));
    currentMain.replaceWith(document.importNode(nextMain,true));
    currentFooter.replaceWith(document.importNode(nextFooter,true));
    document.title=doc.title||document.title;
    document.documentElement.lang=doc.documentElement.lang||document.documentElement.lang;
    document.body.className=doc.body.className||'';
    const nextDescription=doc.querySelector('meta[name="description"]')?.content;
    const currentDescription=document.querySelector('meta[name="description"]');
    if(nextDescription&&currentDescription) currentDescription.content=nextDescription;

    if(push) history.pushState({paiRoute:true,scrollX:0,scrollY:0},'',target.pathname+target.search+target.hash);
    bindMenuToggle();
    ensureLanguageLink();
    normalizeCopy();
    await initPublications();
    settleScroll(target,restore);
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
      if(target.hash){
        saveScroll();
        history.pushState({paiRoute:true,scrollX:0,scrollY:0},'',target.pathname+target.search+target.hash);
        document.getElementById(decodeURIComponent(target.hash.slice(1)))?.scrollIntoView();
        saveScroll();
      }
      return;
    }

    try{ await renderPage(target,true,null); }catch(_e){}
  },true);

  window.addEventListener('popstate',async event=>{
    try{ await renderPage(new URL(location.href),false,event.state||null); }catch(_e){}
  });

  initPublications();
})();
