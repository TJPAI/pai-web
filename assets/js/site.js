const menuBtn=document.querySelector('.menu-btn');
const mobileMenu=document.querySelector('.mobile-menu');
if(menuBtn&&mobileMenu){menuBtn.addEventListener('click',()=>{const open=mobileMenu.classList.toggle('open');menuBtn.setAttribute('aria-expanded',open?'true':'false');});}

(function(){
  const base='https://tjpai.github.io/pai-web';
  let path=location.pathname.replace(/^\/pai-web/,'')||'/';
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
    '/contact.html':'/en/contact.html'
  };
  const reverse=Object.fromEntries(Object.entries(map).map(([zh,en])=>[en,zh]));
  const canonical=base+path;
  const counterpart=base+(isEn?(reverse[path]||'/'):(map[path]||'/en/'));
  const add=(tag,attrs)=>{const el=document.createElement(tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));document.head.appendChild(el);};
  if(!document.querySelector('link[rel="canonical"]')) add('link',{rel:'canonical',href:canonical});
  if(!document.querySelector('link[hreflang]')){
    add('link',{rel:'alternate',hreflang:isEn?'en':'zh-CN',href:canonical});
    add('link',{rel:'alternate',hreflang:isEn?'zh-CN':'en',href:counterpart});
    add('link',{rel:'alternate',hreflang:'x-default',href:base+'/'});
  }
  const title=document.title||'PAI Research Center';
  const description=document.querySelector('meta[name="description"]')?.content||'PAI Research Center at Tongji University.';
  const meta=(property,content)=>{if(!document.querySelector(`meta[property="${property}"]`)) add('meta',{property,content});};
  meta('og:type','website');meta('og:title',title);meta('og:description',description);meta('og:url',canonical);meta('og:site_name','PAI Research Center · Tongji University');
})();
