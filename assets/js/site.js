(function(){
  'use strict';

  const previewHost='tjpai.github.io';
  const isPreview=location.hostname===previewHost;
  const prefix=isPreview?'/pai-web':'';
  const root=path=>`${prefix}${path}`;
  const absolute=path=>new URL(root(path),location.origin).href;

  const normalizedPath=()=>{
    let path=location.pathname;
    if(prefix&&path.startsWith(prefix)) path=path.slice(prefix.length)||'/';
    if(path==='/index.html') return '/';
    if(path==='/en/index.html') return '/en/';
    return path;
  };

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

  const ensureAppStyles=()=>{
    const href=absolute('/assets/css/app.css');
    if([...document.querySelectorAll('link[rel="stylesheet"]')].some(link=>link.href===href)) return;
    const link=document.createElement('link');
    link.rel='stylesheet';
    link.href=href;
    document.head.appendChild(link);
  };
  ensureAppStyles();

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

  const navItems=lang=>lang==='en'?
    [
      ['About','/en/about.html'],['People','/en/team.html'],['Research','/en/research.html'],
      ['Publications','/en/publications.html'],['Join','/en/join.html'],['Contact','/en/contact.html']
    ]:
    [
      ['关于我们','/about.html'],['研究团队','/team.html'],['研究方向','/research.html'],
      ['研究成果','/publications.html'],['人才招聘','/join.html'],['联系我们','/contact.html']
    ];

  const sectionForPath=path=>{
    if(path.includes('/people/')) return 'team';
    if(path.endsWith('/about.html')||path==='/about.html') return 'about';
    if(path.endsWith('/team.html')||path==='/team.html') return 'team';
    if(path.endsWith('/research.html')||path==='/research.html') return 'research';
    if(path.endsWith('/publications.html')||path==='/publications.html') return 'publications';
    if(path.endsWith('/join.html')||path==='/join.html') return 'join';
    if(path.endsWith('/contact.html')||path==='/contact.html') return 'contact';
    return '';
  };

  const counterpartFor=path=>{
    const isEn=path.startsWith('/en/');
    return isEn?(reverseLanguageMap[path]||'/'):(languageMap[path]||'/en/');
  };

  const renderChrome=()=>{
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    const active=sectionForPath(path);
    const header=document.querySelector('.site-header');
    if(header){
      const brand=header.querySelector('.brand');
      if(brand) brand.href=root(lang==='en'?'/en/':'/');

      const nav=header.querySelector('.nav-links');
      const items=navItems(lang);
      const languageLabel=lang==='en'?'中文':'EN';
      const languageHref=counterpartFor(path);
      const markup=items.map(([label,href])=>{
        const key=sectionForPath(href);
        return `<a${key===active?' class="active"':''} href="${root(href)}">${label}</a>`;
      }).join('')+`<a href="${root(languageHref)}">${languageLabel}</a>`;
      if(nav) nav.innerHTML=markup;

      let mobile=header.querySelector('.mobile-menu');
      if(!mobile){
        mobile=document.createElement('nav');
        mobile.className='mobile-menu';
        header.appendChild(mobile);
      }
      mobile.innerHTML=markup;
      mobile.classList.remove('open');

      const button=header.querySelector('.menu-btn');
      if(button){
        button.type='button';
        button.setAttribute('aria-expanded','false');
        button.setAttribute('aria-label',lang==='en'?'Open menu':'打开菜单');
      }
    }

    const footer=document.querySelector('.site-footer');
    if(footer){
      const items=navItems(lang);
      const languageLabel=lang==='en'?'中文':'EN';
      const links=items.map(([label,href])=>`<a href="${root(href)}">${label}</a>`).join('')+
        `<a href="${root(counterpartFor(path))}">${languageLabel}</a>`;
      const contact=lang==='en'?
        `4800 Cao'an Highway, Jiading District, Shanghai<br>Tongji University Jiading Campus<br><a href="mailto:23666042@tongji.edu.cn">23666042@tongji.edu.cn</a>`:
        `上海市嘉定区曹安公路4800号<br>同济大学嘉定校区智信馆<br><a href="mailto:23666042@tongji.edu.cn">23666042@tongji.edu.cn</a>`;
      footer.classList.add('compact-footer');
      footer.innerHTML=`<div class="container"><div class="footer-grid"><div><div class="brand"><strong>PAI</strong><span>PAI Research Center · Tongji University</span></div></div><div class="footer-links">${links}</div><div class="footer-contact">${contact}</div></div><div class="footer-meta"><span>© PAI Research Center</span></div></div>`;
    }
  };

  renderChrome();

  document.addEventListener('click',event=>{
    const button=event.target.closest&&event.target.closest('.menu-btn');
    if(!button) return;
    event.preventDefault();
    const header=button.closest('.site-header');
    const menu=header&&header.querySelector('.mobile-menu');
    if(!menu) return;
    const open=!menu.classList.contains('open');
    menu.classList.toggle('open',open);
    button.setAttribute('aria-expanded',open?'true':'false');
  },true);

  document.addEventListener('click',event=>{
    const link=event.target.closest&&event.target.closest('a');
    if(!link) return;
    const label=(link.textContent||'').trim();
    try{
      if(label==='EN') localStorage.setItem('pai-lang','en');
      else if(label==='中文') localStorage.setItem('pai-lang','zh');
    }catch(_e){}
  },true);

  let siteReady=Promise.resolve();
  if('serviceWorker' in navigator){
    siteReady=(async()=>{
      try{
        const registration=await navigator.serviceWorker.register(root('/sw.js'),{updateViaCache:'none'});
        await navigator.serviceWorker.ready;
        try{
          if(sessionStorage.getItem('pai-sw-checked')!=='1'){
            sessionStorage.setItem('pai-sw-checked','1');
            registration.update().catch(()=>{});
          }
        }catch(_e){}
      }catch(_e){}
    })();
  }

  const responseFor=async url=>{
    try{
      const response=await fetch(url.href,{credentials:'same-origin',cache:'no-store'});
      return response&&response.ok?response:null;
    }catch(_e){
      return null;
    }
  };

  let publicationDataPromise=null;
  const jsonFor=async path=>{
    const response=await responseFor(new URL(absolute(path)));
    if(!response) throw new Error('resource unavailable');
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

  const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[char]));
  const doiHref=doi=>'https://doi.org/'+String(doi).trim().split('/').map(encodeURIComponent).join('/');
  const getExpandedYears=()=>[...document.querySelectorAll('.pub-group[data-expanded="true"]')]
    .map(element=>element.dataset.year).filter(Boolean);

  const updateBackTopVisibility=()=>{
    const button=document.querySelector('[data-pub-back-top]');
    if(button) button.classList.toggle('visible',window.scrollY>700);
  };

  const initPublications=async(expandedYears=[])=>{
    const host=document.querySelector('[data-publications]');
    if(!host) return;
    try{
      const items=await getPublicationData();
      const byYear=new Map();
      for(const item of items){
        if(!byYear.has(item.year)) byYear.set(item.year,[]);
        byYear.get(item.year).push(item);
      }
      const en=(document.documentElement.lang||'').toLowerCase().startsWith('en');
      const expanded=new Set((expandedYears||[]).map(String));
      const fragment=document.createDocumentFragment();

      const years=[...byYear.keys()];
      const yearNav=document.createElement('nav');
      yearNav.className='publication-years';
      yearNav.setAttribute('aria-label',en?'Publication years':'论文年份');
      for(const year of years){
        const button=document.createElement('button');
        button.type='button';
        button.className='publication-year-link';
        button.dataset.pubYearJump=String(year);
        button.textContent=String(year);
        yearNav.appendChild(button);
      }
      fragment.appendChild(yearNav);

      for(const [year,pubs] of byYear){
        const section=document.createElement('section');
        section.className='pub-group';
        section.id=`pub-year-${year}`;
        section.dataset.year=String(year);
        const isExpanded=expanded.has(String(year));
        section.dataset.expanded=isExpanded?'true':'false';
        const count=`${pubs.length} publication${pubs.length===1?'':'s'}`;
        section.innerHTML=`<div class="pub-year-row"><h2 class="pub-year">${year}</h2><span>${count}</span></div>`;

        pubs.forEach((publication,index)=>{
          const article=document.createElement('article');
          article.className='pub'+(!isExpanded&&index>=4?' is-collapsed':'');
          article.dataset.pubExtra=index>=4?'1':'0';
          const actions=publication.doi?
            `<div class="pub-actions"><a href="${esc(doiHref(publication.doi))}" target="_blank" rel="noopener">DOI ↗</a></div>`:'';
          article.innerHTML=`<h3>${esc(publication.title)}</h3><p class="pub-authors">${esc(publication.authors)}</p><p class="pub-venue">${esc(publication.venue)} · ${year}</p>${actions}`;
          section.appendChild(article);
        });

        if(pubs.length>4){
          const toggle=document.createElement('button');
          toggle.type='button';
          toggle.className='pub-toggle';
          toggle.dataset.pubToggle=String(year);
          toggle.setAttribute('aria-expanded',isExpanded?'true':'false');
          toggle.textContent=isExpanded?(en?'Show less ↑':'收起 ↑'):(en?`View all ${pubs.length} ↓`:`展开全部 ${pubs.length} 篇 ↓`);
          section.appendChild(toggle);
        }
        fragment.appendChild(section);
      }

      const top=document.createElement('button');
      top.type='button';
      top.className='pub-back-top';
      top.dataset.pubBackTop='1';
      top.textContent=en?'↑ Top':'↑ 顶部';
      fragment.appendChild(top);

      host.replaceChildren(fragment);
      host.dataset.paiInitialized='1';
      updateBackTopVisibility();
    }catch(_e){
      const en=(document.documentElement.lang||'').toLowerCase().startsWith('en');
      host.innerHTML=`<p class="muted">${en?'Publications are temporarily unavailable. Please try again later.':'论文数据暂时无法载入，请稍后再试。'}</p>`;
    }
  };

  document.addEventListener('click',event=>{
    const jump=event.target.closest&&event.target.closest('[data-pub-year-jump]');
    if(jump){
      event.preventDefault();
      document.getElementById(`pub-year-${jump.dataset.pubYearJump}`)?.scrollIntoView({behavior:'smooth',block:'start'});
      return;
    }

    const toggle=event.target.closest&&event.target.closest('[data-pub-toggle]');
    if(toggle){
      event.preventDefault();
      const section=toggle.closest('.pub-group');
      if(!section) return;
      const open=section.dataset.expanded!=='true';
      section.dataset.expanded=open?'true':'false';
      section.querySelectorAll('.pub[data-pub-extra="1"]').forEach(article=>article.classList.toggle('is-collapsed',!open));
      const count=section.querySelectorAll('.pub').length;
      const en=(document.documentElement.lang||'').toLowerCase().startsWith('en');
      toggle.setAttribute('aria-expanded',open?'true':'false');
      toggle.textContent=open?(en?'Show less ↑':'收起 ↑'):(en?`View all ${count} ↓`:`展开全部 ${count} 篇 ↓`);
      saveScroll(true);
      return;
    }

    const top=event.target.closest&&event.target.closest('[data-pub-back-top]');
    if(top){
      event.preventDefault();
      window.scrollTo({top:0,behavior:'smooth'});
    }
  },true);

  const addHead=(tag,attrs)=>{
    const element=document.createElement(tag);
    Object.entries(attrs).forEach(([key,value])=>element.setAttribute(key,value));
    document.head.appendChild(element);
    return element;
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

  try{ history.scrollRestoration='manual'; }catch(_e){}
  let transitioning=false;
  let scrollTick=0;
  let navigationSeq=0;

  const saveScroll=(force=false)=>{
    if(transitioning&&!force) return;
    try{
      history.replaceState(Object.assign({},history.state||{},{
        paiRoute:true,
        scrollX:window.scrollX,
        scrollY:window.scrollY,
        pubExpanded:getExpandedYears()
      }),'',location.href);
    }catch(_e){}
  };

  if(!history.state||history.state.paiRoute!==true){
    try{
      history.replaceState({paiRoute:true,scrollX:window.scrollX,scrollY:window.scrollY,pubExpanded:getExpandedYears()},'',location.href);
    }catch(_e){}
  }

  window.addEventListener('scroll',()=>{
    updateBackTopVisibility();
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
      setTimeout(()=>{apply();resolve();},140);
    }));
  });

  const renderPage=async(target,{push=true,restoreState=null,seq=0}={})=>{
    const requestUrl=new URL(target.href);
    requestUrl.hash='';
    const response=await responseFor(requestUrl);
    if(!response||seq!==navigationSeq) return false;

    const doc=new DOMParser().parseFromString(await response.text(),'text/html');
    const nextMain=doc.querySelector('main');
    const currentMain=document.querySelector('main');
    if(!nextMain||!currentMain||seq!==navigationSeq) return false;

    currentMain.replaceWith(document.importNode(nextMain,true));
    document.documentElement.lang=doc.documentElement.lang||document.documentElement.lang;
    document.body.className=doc.body.className||'';
    updateMetadata(doc,target);

    if(push){
      history.pushState({paiRoute:true,scrollX:0,scrollY:0,pubExpanded:[]},'',target.pathname+target.search+target.hash);
    }

    renderChrome();
    await initPublications(restoreState?.pubExpanded||[]);
    if(seq!==navigationSeq) return false;
    await restorePosition(target,restoreState);
    return true;
  };

  const isRouteableInternal=link=>{
    if(!link||link.target==='_blank'||link.hasAttribute('download')) return false;
    const raw=link.getAttribute('href')||'';
    if(!raw||raw.startsWith('mailto:')||raw.startsWith('tel:')||raw.startsWith('javascript:')) return false;
    const target=new URL(link.href,location.href);
    if(target.origin!==location.origin) return false;
    if(prefix&&!target.pathname.startsWith(prefix)) return false;
    return target.pathname.endsWith('/')||target.pathname.endsWith('.html');
  };

  document.addEventListener('click',async event=>{
    if(event.defaultPrevented||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    if(typeof event.button==='number'&&event.button!==0) return;
    const link=event.target.closest&&event.target.closest('a');
    if(!isRouteableInternal(link)) return;

    const target=new URL(link.href,location.href);
    event.preventDefault();

    const menu=document.querySelector('.site-header .mobile-menu');
    const button=document.querySelector('.site-header .menu-btn');
    menu?.classList.remove('open');
    button?.setAttribute('aria-expanded','false');

    const currentNoHash=location.origin+location.pathname+location.search;
    const targetNoHash=target.origin+target.pathname+target.search;

    if(currentNoHash===targetNoHash){
      if(target.hash&&target.hash!==location.hash){
        saveScroll(true);
        history.pushState({paiRoute:true,scrollX:0,scrollY:0,pubExpanded:getExpandedYears()},'',target.pathname+target.search+target.hash);
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
    const seq=++navigationSeq;
    try{
      const ok=await renderPage(target,{push:true,restoreState:null,seq});
      if(!ok&&seq===navigationSeq) location.assign(target.href);
    }catch(_e){
      if(seq===navigationSeq) location.assign(target.href);
    }finally{
      if(seq===navigationSeq){
        transitioning=false;
        saveScroll(true);
      }
    }
  },true);

  window.addEventListener('popstate',async event=>{
    transitioning=true;
    const seq=++navigationSeq;
    try{
      const ok=await renderPage(new URL(location.href),{push:false,restoreState:event.state||null,seq});
      if(!ok&&seq===navigationSeq) location.reload();
    }catch(_e){
      if(seq===navigationSeq) location.reload();
    }finally{
      if(seq===navigationSeq){
        transitioning=false;
        saveScroll(true);
      }
    }
  });

  initPublications(history.state?.pubExpanded||[]);
  siteReady.catch(()=>{});
})();
