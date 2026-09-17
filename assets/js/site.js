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
  const root=(p)=>`${prefix}${p}`;
  const addHead=(tag,attrs)=>{const el=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));document.head.appendChild(el);return el;};

  const nav=document.querySelector('.site-header .nav');
  const navLinks=document.querySelector('.nav-links');
  const menuBtn=document.querySelector('.menu-btn');
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

  if(menuBtn&&mobileMenu){
    if(!menuBtn.hasAttribute('aria-expanded')) menuBtn.setAttribute('aria-expanded','false');
    menuBtn.addEventListener('click',()=>{
      const open=mobileMenu.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded',open?'true':'false');
    });
  }

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
})();
