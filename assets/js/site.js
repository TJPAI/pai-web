(function(){
  const previewHost='tjpai.github.io';
  const isPreview=location.hostname===previewHost;
  const prefix=isPreview?'/pai-web':'';
  const base=location.origin+prefix;
  const root=p=>`${prefix}${p}`;
  let siteCacheReady=Promise.resolve();

  const normalizedPath=()=>{
    let p=location.pathname;
    if(prefix&&p.startsWith(prefix)) p=p.slice(prefix.length)||'/';
    if(p==='/index.html') p='/';
    if(p==='/en/index.html') p='/en/';
    return p;
  };

  const initialPath=normalizedPath();
  const initialIsEn=initialPath.startsWith('/en/');

  /* First entry: explicit language choice wins; otherwise follow OS/browser language. */
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
    if(!menuBtn.hasAttribute('aria-expanded')) menuBtn.setAttribute('aria-expanded','false');
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

  bindMenuToggle();
  ensureLanguageLink();

  /* Remember language only when the visitor explicitly switches. */
  document.addEventListener('click',event=>{
    const a=event.target.closest&&event.target.closest('a');
    if(!a) return;
    const label=(a.textContent||'').trim();
    try{
      if(label==='EN') localStorage.setItem('pai-lang','en');
      else if(label==='中文') localStorage.setItem('pai-lang','zh');
    }catch(_e){}
  });

  /* Minimal SEO metadata for directly loaded pages. */
  const addHead=(tag,attrs)=>{const el=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));document.head.appendChild(el);return el;};
  const canonical=base+initialPath;
  if(!document.querySelector('link[rel="canonical"]')) addHead('link',{rel:'canonical',href:canonical});
  const title=document.title||'PAI Research Center';
  const description=document.querySelector('meta[name="description"]')?.content||'PAI Research Center at Tongji University.';
  const meta=(property,content)=>{if(!document.querySelector(`meta[property="${property}"]`)) addHead('meta',{property,content});};
  meta('og:type','website'); meta('og:title',title); meta('og:description',description); meta('og:url',canonical); meta('og:site_name','PAI Research Center · Tongji University');

  /* Install the full-site cache once per browsing session. */
  if('serviceWorker' in navigator){
    siteCacheReady=(async()=>{
      try{
        let registration;
        if(sessionStorage.getItem('pai-sw-checked')==='1') registration=await navigator.serviceWorker.getRegistration(root('/'));
        else{
          registration=await navigator.serviceWorker.register(root('/sw.js'),{updateViaCache:'none'});
          sessionStorage.setItem('pai-sw-checked','1');
        }
        await navigator.serviceWorker.ready;
        if(registration&&registration.waiting) registration.waiting.postMessage({type:'SKIP_WAITING'});
      }catch(_e){}
    })();
  }

  const responseFor=async url=>{
    await siteCacheReady;
    if('caches' in window){
      const names=(await caches.keys()).filter(name=>name.startsWith('pai-site-')).sort().reverse();
      for(const name of names){
        const cache=await caches.open(name);
        let hit=await cache.match(url.href,{ignoreSearch:true});
        if(hit) return hit;
        if(url.pathname.endsWith('/')){
          const indexUrl=new URL(url.href); indexUrl.pathname=url.pathname+'index.html';
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

  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const doiHref=doi=>'https://doi.org/'+String(doi).trim().split('/').map(encodeURIComponent).join('/');

  /* Dynamic page hook: scripts in parsed HTML do not execute after a DOM swap, so initialize them here. */
  const initPublications=async()=>{
    const host=document.querySelector('[data-publications]');
    if(!host||host.dataset.paiInitialized==='1') return;
    host.dataset.paiInitialized='1';
    const en=(document.documentElement.lang||'').toLowerCase().startsWith('en');
    try{
      const [recent,archive]=await Promise.all([
        fetch(root('/data/publications.json')).then(r=>{if(!r.ok) throw new Error(); return r.json();}),
        fetch(root('/data/publications-archive.json')).then(r=>r.ok?r.json():[])
      ]);
      const items=[...recent,...archive].sort((a,b)=>b.year-a.year);
      const byYear=new Map();
      items.forEach(item=>{if(!byYear.has(item.year)) byYear.set(item.year,[]); byYear.get(item.year).push(item);});
      host.innerHTML='';
      for(const [year,pubs] of byYear){
        const section=document.createElement('section');
        section.className='pub-group';
        const count=en?`${pubs.length} publication${pubs.length===1?'':'s'}`:`${pubs.length} publications`;
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

  const renderPage=async(target,push=true)=>{
    const requestUrl=new URL(target.href); requestUrl.hash='';
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

    currentHeader.replaceWith(document.importNode(nextHeader,true));
    currentMain.replaceWith(document.importNode(nextMain,true));
    currentFooter.replaceWith(document.importNode(nextFooter,true));
    document.title=doc.title||document.title;
    document.documentElement.lang=doc.documentElement.lang||document.documentElement.lang;
    document.body.className=doc.body.className||'';
    const nextDescription=doc.querySelector('meta[name="description"]')?.content;
    const currentDescription=document.querySelector('meta[name="description"]');
    if(nextDescription&&currentDescription) currentDescription.content=nextDescription;

    if(push) history.pushState({paiRoute:true},'',target.pathname+target.search+target.hash);
    bindMenuToggle();
    ensureLanguageLink();
    await initPublications();
    if(target.hash){
      const id=decodeURIComponent(target.hash.slice(1));
      requestAnimationFrame(()=>document.getElementById(id)?.scrollIntoView());
    }else window.scrollTo(0,0);
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

  /* Universal same-origin router: header, footer and every in-page internal link use the same no-document-navigation path. */
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
    if(currentNoHash===targetNoHash&&target.hash){
      history.pushState({paiRoute:true},'',target.pathname+target.search+target.hash);
      document.getElementById(decodeURIComponent(target.hash.slice(1)))?.scrollIntoView();
      return;
    }
    try{ await renderPage(target,true); }catch(_e){}
  },true);

  window.addEventListener('popstate',async()=>{
    try{ await renderPage(new URL(location.href),false); }catch(_e){}
  });
})();
