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

  const nav=document.querySelector('.site-header .nav');
  const navLinks=document.querySelector('.nav-links');
  const menuBtn=document.querySelector('.menu-btn');
  let mobileMenu=document.querySelector('.mobile-menu');

  const hasLanguageLink=(root)=>root&&[...root.querySelectorAll('a')].some(a=>/^(EN|中文)$/.test(a.textContent.trim()));
  if(navLinks&&!hasLanguageLink(navLinks)){
    const lang=document.createElement('a');
    lang.href=counterpartPath.startsWith('/')?(prefix||'')+counterpartPath:counterpartPath;
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
    lang.href=counterpartPath.startsWith('/')?(prefix||'')+counterpartPath:counterpartPath;
    lang.textContent=isEn?'中文':'EN';
    mobileMenu.appendChild(lang);
  }

  if(menuBtn&&mobileMenu){
    if(!menuBtn.hasAttribute('aria-expanded')) menuBtn.setAttribute('aria-expanded','false');
    menuBtn.addEventListener('click',()=>{
      const open=mobileMenu.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded',open?'true':'false');
    });
  }

  if(!document.querySelector('link[rel="canonical"]')) addHead('link',{rel:'canonical',href:canonical});
  if(!document.querySelector('link[hreflang]')){
    addHead('link',{rel:'alternate',hreflang:isEn?'en':'zh-CN',href:canonical});
    addHead('link',{rel:'alternate',hreflang:isEn?'zh-CN':'en',href:counterpart});
    addHead('link',{rel:'alternate',hreflang:'x-default',href:base+'/'});
  }
  if(isPreview&&!document.querySelector('meta[name="robots"]')) addHead('meta',{name:'robots',content:'noindex,nofollow'});
  const title=document.title||'PAI Research Center';
  const description=document.querySelector('meta[name="description"]')?.content||'PAI Research Center at Tongji University.';
  const meta=(property,content)=>{if(!document.querySelector(`meta[property="${property}"]`)) addHead('meta',{property,content});};
  meta('og:type','website');meta('og:title',title);meta('og:description',description);meta('og:url',canonical);meta('og:site_name','PAI Research Center · Tongji University');
})();
