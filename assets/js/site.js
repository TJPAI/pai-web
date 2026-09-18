(function(){
  const previewHost='tjpai.github.io';
  const isPreview=location.hostname===previewHost;
  const prefix=isPreview?'/pai-web':'';
  const base=location.origin+prefix;
  let path=location.pathname;
  if(prefix&&path.startsWith(prefix)) path=path.slice(prefix.length)||'/';
  if(path==='/index.html') path='/';
  if(path==='/en/index.html') path='/en/';
  const isEn=path.startsWith('/en/');
  const root=(p)=>`${prefix}${p}`;
  let siteCacheReady=Promise.resolve();

  /* Homepage language selection: explicit user choice wins; otherwise use OS/browser language. */
  try{
    const saved=localStorage.getItem('pai-lang');
    const primary=(navigator.languages&&navigator.languages[0])||navigator.language||'en';
    const preferred=saved||(String(primary).toLowerCase().startsWith('zh')?'zh':'en');
    const isBot=/bot|crawler|spider|slurp/i.test(navigator.userAgent||'');
    if(!isBot&&path==='/'&&preferred==='en'){
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
  const counterpartPath=isEn?(reverse[path]||'/'):(map[path]||'/en/');
  const canonical=base+path;
  const counterpart=base+counterpartPath;
  const addHead=(tag,attrs)=>{const el=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));document.head.appendChild(el);return el;};

  /* Remember a language only when the visitor explicitly switches language. */
  document.addEventListener('click',(event)=>{
    const a=event.target.closest&&event.target.closest('a');
    if(!a) return;
    const label=(a.textContent||'').trim();
    if(label==='EN'){
      try{localStorage.setItem('pai-lang','en');}catch(_e){}
    }else if(label==='中文'){
      try{localStorage.setItem('pai-lang','zh');}catch(_e){}
    }
  });

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

  const nav=document.querySelector('.site-header .nav');
  const navLinks=document.querySelector('.nav-links');
  let mobileMenu=document.querySelector('.mobile-menu');

  const hasLanguageLink=(el)=>el&&[...el.querySelectorAll('a')].some(a=>/^(EN|中文)$/.test(a.textContent.trim()));
  if(navLinks&&!hasLanguageLink(navLinks)){
    const lang=document.createElement('a');
    lang.href=root(counterpartPath);
    lang.textContent=isEn?'中文':'EN';
    navLinks.appendChild(lang);
  }

  if(!mobileMenu&&nav&&navLinks){
    mobileMenu=document.createElement('nav');
    mobileMenu.className='mobile-menu';
    [...navLinks.querySelectorAll('a')].forEach(a=>mobileMenu.appendChild(a.cloneNode(true)));
    nav.insertAdjacentElement('afterend',mobileMenu);
  }else if(mobileMenu&&!hasLanguageLink(mobileMenu)){
    const lang=document.createElement('a');
    lang.href=root(counterpartPath);
    lang.textContent=isEn?'中文':'EN';
    mobileMenu.appendChild(lang);
  }

  bindMenuToggle();

  if(isEn&&path.startsWith('/en/people/')){
    const footer=document.querySelector('.site-footer.compact-footer');
    if(footer&&!footer.querySelector('.footer-grid')){
      footer.innerHTML=`<div class="container"><div class="footer-grid"><div><div class="brand"><strong>PAI</strong><span>PAI Research Center · Tongji University</span></div></div><div class="footer-links"><a href="${root('/en/about.html')}">About</a><a href="${root('/en/research.html')}">Research</a><a href="${root('/en/team.html')}">People</a><a href="${root('/en/publications.html')}">Publications</a><a href="${root('/en/join.html')}">Join</a><a href="${root('/en/contact.html')}">Contact</a><a href="${root(counterpartPath)}">中文</a></div><div class="footer-contact">Zhixin Building, Tongji University Jiading Campus<br>4800 Cao'an Highway, Jiading District, Shanghai<br><a href="mailto:23666042@tongji.edu.cn">23666042@tongji.edu.cn</a></div></div><div class="footer-meta"><span>© PAI Research Center</span></div></div>`;
    }
  }

  const robots=document.querySelector('meta[name="robots"]');
  const isNoIndex=robots&&/\bnoindex\b/i.test(robots.content||'');
  if(isPreview&&!robots) addHead('meta',{name:'robots',content:'noindex,nofollow'});
  if(!isNoIndex){
    if(!document.querySelector('link[rel="canonical"]')) addHead('link',{rel:'canonical',href:canonical});
    if(!document.querySelector('link[hreflang]')){
      addHead('link',{rel:'alternate',hreflang:isEn?'en':'zh-CN',href:canonical});
      addHead('link',{rel:'alternate',hreflang:isEn?'zh-CN':'en',href:counterpart});
      addHead('link',{rel:'alternate',hreflang:'x-default',href:base+'/'});
    }
  }
  const title=document.title||'PAI Research Center';
  const description=document.querySelector('meta[name="description"]')?.content||'PAI Research Center at Tongji University.';
  const meta=(property,content)=>{if(!document.querySelector(`meta[property="${property}"]`)) addHead('meta',{property,content});};
  meta('og:type','website');meta('og:title',title);meta('og:description',description);meta('og:url',canonical);meta('og:site_name','PAI Research Center · Tongji University');

  /* Install/cache once, then let the browser check sw.js once per browsing session for updates. */
  if('serviceWorker' in navigator){
    siteCacheReady=(async()=>{
      try{
        let registration;
        if(sessionStorage.getItem('pai-sw-checked')==='1'){
          registration=await navigator.serviceWorker.getRegistration(root('/'));
        }else{
          registration=await navigator.serviceWorker.register(root('/sw.js'),{updateViaCache:'none'});
          sessionStorage.setItem('pai-sw-checked','1');
        }
        await navigator.serviceWorker.ready;
        if(registration&&registration.waiting) registration.waiting.postMessage({type:'SKIP_WAITING'});
      }catch(_e){}
    })();
  }

  /*
   * App-like menu navigation.
   * Header/footer navigation is rendered from the pre-cached HTML with History API,
   * so Safari/Chrome does not perform a document navigation or show its loading bar.
   */
  const cachedResponseFor=async(url)=>{
    await siteCacheReady;
    if(!('caches' in window)) return null;
    const names=(await caches.keys()).filter(name=>name.startsWith('pai-site-'));
    for(let i=names.length-1;i>=0;i--){
      const cache=await caches.open(names[i]);
      const hit=await cache.match(url.href,{ignoreSearch:true});
      if(hit) return hit;
      if(url.pathname.endsWith('/')){
        const indexUrl=new URL(url.href);
        indexUrl.pathname=url.pathname+'index.html';
        const indexHit=await cache.match(indexUrl.href,{ignoreSearch:true});
        if(indexHit) return indexHit;
      }
    }
    return null;
  };

  const renderCachedPage=async(target,push)=>{
    const response=await cachedResponseFor(target);
    if(!response) return false;
    const html=await response.text();
    const doc=new DOMParser().parseFromString(html,'text/html');
    const nextHeader=doc.querySelector('.site-header');
    const nextMain=doc.querySelector('main');
    const nextFooter=doc.querySelector('.site-footer');
    if(!nextHeader||!nextMain||!nextFooter) return false;

    const currentHeader=document.querySelector('.site-header');
    const currentMain=document.querySelector('main');
    const currentFooter=document.querySelector('.site-footer');
    if(!currentHeader||!currentMain||!currentFooter) return false;

    currentHeader.replaceWith(document.importNode(nextHeader,true));
    currentMain.replaceWith(document.importNode(nextMain,true));
    currentFooter.replaceWith(document.importNode(nextFooter,true));
    document.title=doc.title||document.title;
    document.documentElement.lang=doc.documentElement.lang||document.documentElement.lang;
    document.body.className=doc.body.className||'';

    const nextDescription=doc.querySelector('meta[name="description"]')?.content;
    const currentDescription=document.querySelector('meta[name="description"]');
    if(nextDescription&&currentDescription) currentDescription.content=nextDescription;
    const canonicalLink=document.querySelector('link[rel="canonical"]');
    if(canonicalLink) canonicalLink.href=target.href;
    const ogUrl=document.querySelector('meta[property="og:url"]');
    if(ogUrl) ogUrl.content=target.href;
    const ogTitle=document.querySelector('meta[property="og:title"]');
    if(ogTitle) ogTitle.content=document.title;
    if(push) history.pushState({paiCachedRoute:true},'',target.href);
    bindMenuToggle();
    window.scrollTo(0,0);
    return true;
  };

  const isAppMenuLink=(a)=>!!a.closest('.site-header,.site-footer');
  document.addEventListener('click',async(event)=>{
    if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    const a=event.target.closest&&event.target.closest('a');
    if(!a||!isAppMenuLink(a)||a.target==='_blank'||a.hasAttribute('download')) return;
    const href=a.getAttribute('href')||'';
    if(!href||href.startsWith('#')||href.startsWith('mailto:')||href.startsWith('tel:')||href.startsWith('javascript:')) return;
    const target=new URL(a.href,location.href);
    if(target.origin!==location.origin) return;
    event.preventDefault();
    try{
      const rendered=await renderCachedPage(target,true);
      if(!rendered) location.href=target.href;
    }catch(_e){
      location.href=target.href;
    }
  });

  window.addEventListener('popstate',async()=>{
    const target=new URL(location.href);
    try{
      const rendered=await renderCachedPage(target,false);
      if(!rendered) location.reload();
    }catch(_e){
      location.reload();
    }
  });
})();
