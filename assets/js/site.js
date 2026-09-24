(function(){
  'use strict';

  const previewHost='tjpai.github.io';
  const isPreview=location.hostname===previewHost;
  const prefix=isPreview?'/pai-web':'';
  const root=path=>`${prefix}${path}`;
  const absolute=path=>new URL(root(path),location.origin).href;
  const PUB_VISIBLE_DEFAULT=3;

  const normalizedPath=(pathname=location.pathname)=>{
    let path=pathname||'/';
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

  const navItems=lang=>lang==='en'?
    [
      ['About','/en/about.html'],['People','/en/team.html'],['Research','/en/research.html'],
      ['Outputs','/en/publications.html'],['Join','/en/join.html'],['Contact','/en/contact.html']
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

  const sharedAnchors={
    about:new Set(['about','overview','collaboration','achievements','international-impact']),
    research:new Set(['pnl','iotng','aibi']),
    contact:new Set(['cooperation','recruitment'])
  };

  const counterpartWithContext=path=>{
    const counterpart=counterpartFor(path);
    const section=sectionForPath(path);
    const hash=location.hash?decodeURIComponent(location.hash.slice(1)):'';
    if(hash&&sharedAnchors[section]?.has(hash)) return `${counterpart}#${encodeURIComponent(hash)}`;
    return counterpart;
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

  const renderChrome=()=>{
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    const active=sectionForPath(path);
    const items=navItems(lang);
    const languageLabel=lang==='en'?'中文':'EN';
    const languageHref=counterpartWithContext(path);
    const markup=items.map(([label,href])=>{
      const key=sectionForPath(href);
      return `<a${key===active?' class="active" aria-current="page"':''} href="${root(href)}">${label}</a>`;
    }).join('')+`<a href="${root(languageHref)}">${languageLabel}</a>`;

    const header=document.querySelector('.site-header');
    if(header){
      const brand=header.querySelector('.brand');
      if(brand) brand.href=root(lang==='en'?'/en/':'/');
      const nav=header.querySelector('.nav-links');
      let mobile=header.querySelector('.mobile-menu');
      if(!mobile){
        mobile=document.createElement('nav');
        mobile.className='mobile-menu';
        header.appendChild(mobile);
      }

      const needsRebuild=header.dataset.paiLang!==lang||!nav||!nav.querySelector('a')||!mobile.querySelector('a');
      if(needsRebuild){
        if(nav) nav.innerHTML=markup;
        mobile.innerHTML=markup;
        header.dataset.paiLang=lang;
      }else{
        const syncLinks=container=>{
          if(!container) return;
          [...container.querySelectorAll('a')].forEach(link=>{
            const label=(link.textContent||'').trim();
            const isLanguage=label==='EN'||label==='中文';
            if(isLanguage){
              link.href=root(languageHref);
              link.classList.remove('active');
              link.removeAttribute('aria-current');
              return;
            }
            let key='';
            try{ key=sectionForPath(normalizedPath(new URL(link.href,location.href).pathname)); }catch(_e){}
            const isActive=!!active&&key===active;
            link.classList.toggle('active',isActive);
            if(isActive) link.setAttribute('aria-current','page');
            else link.removeAttribute('aria-current');
          });
        };
        syncLinks(nav);
        syncLinks(mobile);
      }

      if(nav) nav.setAttribute('aria-label',lang==='en'?'Main navigation':'主导航');
      mobile.id='mobile-navigation';
      mobile.setAttribute('aria-label',lang==='en'?'Mobile navigation':'移动导航');
      mobile.classList.remove('open');
      const button=header.querySelector('.menu-btn');
      if(button){
        button.type='button';
        button.setAttribute('aria-expanded','false');
        button.setAttribute('aria-controls','mobile-navigation');
        button.setAttribute('aria-label',lang==='en'?'Open menu':'打开菜单');
      }
    }

    const footer=document.querySelector('.site-footer');
    if(footer){
      const links=items.map(([label,href])=>`<a href="${root(href)}">${label}</a>`).join('')+
        `<a href="${root(languageHref)}">${languageLabel}</a>`;
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
    const menu=button.closest('.site-header')?.querySelector('.mobile-menu');
    if(!menu) return;
    const open=!menu.classList.contains('open');
    menu.classList.toggle('open',open);
    button.setAttribute('aria-expanded',open?'true':'false');
  },true);

  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape') return;
    const header=document.querySelector('.site-header');
    const menu=header?.querySelector('.mobile-menu');
    const button=header?.querySelector('.menu-btn');
    if(!menu?.classList.contains('open')) return;
    menu.classList.remove('open');
    if(button){ button.setAttribute('aria-expanded','false'); button.focus(); }
  });

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
    siteReady=navigator.serviceWorker.getRegistrations().then(rs=>Promise.all(rs.map(r=>r.unregister()))).catch(()=>{});
  }

  const pageCache=new Map([[location.href.split('#')[0],document.documentElement.outerHTML]]);
  let navigating=false;
  let scrollSaveTimer=null;

  try{ history.scrollRestoration='manual'; }catch(_e){}
  const historyStateWithScroll=scrollY=>Object.assign({},history.state||{},{pai:true,scrollY});
  const scrollToInstant=y=>{
    const rootStyle=document.documentElement.style;
    const previous=rootStyle.scrollBehavior;
    rootStyle.scrollBehavior='auto';
    window.scrollTo(0,Math.max(0,Number(y)||0));
    requestAnimationFrame(()=>{ rootStyle.scrollBehavior=previous; });
  };
  const PAGE_SCROLL_KEY='pai-page-scroll-v1';
  let pageScrollPositions={};
  try{ pageScrollPositions=JSON.parse(sessionStorage.getItem(PAGE_SCROLL_KEY)||'{}')||{}; }catch(_e){}
  const rememberPageScroll=(path,y)=>{
    const value=Math.max(0,Math.round(Number(y)||0));
    pageScrollPositions[path]=value;
    try{ sessionStorage.setItem(PAGE_SCROLL_KEY,JSON.stringify(pageScrollPositions)); }catch(_e){}
    return value;
  };
  const rememberedPageScroll=path=>Math.max(0,Number(pageScrollPositions[path])||0);
  const destinationScrollForPath=path=>rememberedPageScroll(path);
  const cacheCurrentPageSnapshot=()=>{
    try{
      const snapshot=document.documentElement.cloneNode(true);
      const snapshotMain=snapshot.querySelector('main');
      if(snapshotMain){
        snapshotMain.style.removeProperty('transform');
        snapshotMain.style.removeProperty('will-change');
        snapshotMain.style.removeProperty('opacity');
      }
      pageCache.set(location.href.split('#')[0],snapshot.outerHTML);
    }catch(_e){}
  };
  const saveCurrentScroll=()=>{
    if(navigating) return;
    const y=rememberPageScroll(normalizedPath(),window.scrollY);
    try{ history.replaceState(historyStateWithScroll(y),'',location.href); }catch(_e){}
  };
  saveCurrentScroll();
  addEventListener('scroll',()=>{
    if(scrollSaveTimer!==null) return;
    scrollSaveTimer=setTimeout(()=>{
      scrollSaveTimer=null;
      saveCurrentScroll();
    },120);
  },{passive:true});

  const fetchPage=async url=>{
    const key=url.href.split('#')[0];
    if(pageCache.has(key)) return pageCache.get(key);
    const response=await fetch(key,{credentials:'same-origin'});
    if(!response.ok) throw new Error('page unavailable');
    const html=await response.text();
    pageCache.set(key,html);
    return html;
  };

  const applyPage=async(url,{historyMode='push',preserveScrollY=null,transitionDirection=0,gestureOffset=0}={})=>{
    if(navigating) return;
    if(scrollSaveTimer!==null){
      clearTimeout(scrollSaveTimer);
      scrollSaveTimer=null;
    }
    navigating=true;
    try{
      const html=await fetchPage(url);
      const next=new DOMParser().parseFromString(html,'text/html');
      const currentMain=document.querySelector('main');
      const nextMain=next.querySelector('main');
      if(!currentMain||!nextMain) throw new Error('page shell unavailable');

      const reduceMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
      const animateMain=async(node,keyframes,options)=>{
        if(!node||reduceMotion||!transitionDirection||typeof node.animate!=='function') return;
        try{
          const animation=node.animate(keyframes,options);
          await animation.finished;
        }catch(_e){}
      };
      const shift=transitionDirection>0?-18:18;
      const startShift=transitionDirection?Math.max(-18,Math.min(18,Number(gestureOffset)||0)):0;
      currentMain.style.willChange='transform, opacity';
      await animateMain(currentMain,[
        {transform:`translate3d(${startShift}px,0,0)`,opacity:1},
        {transform:`translate3d(${shift}px,0,0)`,opacity:.9}
      ],{duration:105,easing:'cubic-bezier(.4,0,1,1)',fill:'forwards'});

      const destinationScroll=Number.isFinite(preserveScrollY)?preserveScrollY:0;
      if(historyMode==='push') history.pushState({pai:true,scrollY:destinationScroll},'',url.href);
      else if(historyMode==='replace') history.replaceState({pai:true,scrollY:destinationScroll},'',url.href);

      const incomingMain=document.importNode(nextMain,true);
      currentMain.replaceWith(incomingMain);
      document.title=next.title||document.title;
      document.documentElement.lang=next.documentElement.lang||document.documentElement.lang;
      document.body.className=next.body.className;

      renderChrome();

      const hasRequestedScroll=Number.isFinite(preserveScrollY);
      if(hasRequestedScroll){
        const provisionalMaxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        scrollToInstant(Math.min(Math.max(0,preserveScrollY),provisionalMaxY));
      }else if(!url.hash){
        scrollToInstant(0);
      }

      const preservedPublicationYears=[...next.querySelectorAll('.pub-group[data-expanded="true"]')]
        .map(section=>section.dataset.year).filter(Boolean);
      await initPublications(preservedPublicationYears);
      setTimeout(()=>warmNavigation(),80);
      await new Promise(resolve=>requestAnimationFrame(resolve));
      if(hasRequestedScroll){
        const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        const restoredY=Math.min(Math.max(0,preserveScrollY),maxY);
        if(Math.abs(window.scrollY-restoredY)>1) scrollToInstant(restoredY);
        rememberPageScroll(normalizedPath(url.pathname),restoredY);
        try{ history.replaceState(historyStateWithScroll(restoredY),'',location.href); }catch(_e){}
      }else if(url.hash){
        document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView();
        const y=rememberPageScroll(normalizedPath(url.pathname),window.scrollY);
        try{ history.replaceState(historyStateWithScroll(y),'',location.href); }catch(_e){}
      }else{
        rememberPageScroll(normalizedPath(url.pathname),0);
        try{ history.replaceState(historyStateWithScroll(0),'',location.href); }catch(_e){}
      }

      if(transitionDirection&&!reduceMotion){
        const incomingShift=transitionDirection>0?18:-18;
        await new Promise(resolve=>requestAnimationFrame(resolve));
        await animateMain(incomingMain,[
          {transform:`translate3d(${incomingShift}px,0,0)`,opacity:.9},
          {transform:'translate3d(0,0,0)',opacity:1}
        ],{duration:175,easing:'cubic-bezier(.2,.72,.22,1)',fill:'both'});
      }
      incomingMain.style.willChange='';
      setTimeout(()=>warmSwipeNeighbors(),40);
    }finally{
      navigating=false;
    }
  };

  const eligiblePageLink=link=>{
    if(!link||link.target||link.hasAttribute('download')) return null;
    const href=link.getAttribute('href');
    if(!href||href.startsWith('#')||/^(mailto:|tel:|javascript:)/i.test(href)) return null;
    const url=new URL(link.href,location.href);
    if(url.origin!==location.origin) return null;
    if(!/\/$|\.html$/i.test(url.pathname)) return null;
    return url;
  };

  document.addEventListener('click',event=>{
    if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    const link=event.target.closest&&event.target.closest('a');
    const url=eligiblePageLink(link);
    if(!url) return;
    event.preventDefault();
    const mobileMenu=link.closest('.mobile-menu');
    if(mobileMenu){
      mobileMenu.classList.remove('open');
      const button=mobileMenu.closest('.site-header')?.querySelector('.menu-btn');
      if(button) button.setAttribute('aria-expanded','false');
    }
    saveCurrentScroll();
    cacheCurrentPageSnapshot();
    const label=(link.textContent||'').trim();
    const isLanguageSwitch=label==='EN'||label==='中文';
    let options;
    if(isLanguageSwitch){
      options={preserveScrollY:window.scrollY};
    }else if(!url.hash){
      options={preserveScrollY:destinationScrollForPath(normalizedPath(url.pathname))};
    }
    applyPage(url,options).catch(()=>{ location.href=url.href; });
  });

  addEventListener('popstate',event=>{
    const restoredY=Number.isFinite(event.state?.scrollY)?event.state.scrollY:0;
    applyPage(new URL(location.href),{historyMode:'none',preserveScrollY:restoredY}).catch(()=>location.reload());
  });

  const warmNavigation=()=>{
    if(navigator.connection&&navigator.connection.saveData) return;
    const seen=new Set();
    [...document.querySelectorAll('a[href]')].forEach((link,index)=>{
      const url=eligiblePageLink(link);
      if(!url) return;
      const key=url.href.split('#')[0];
      if(seen.has(key)) return;
      seen.add(key);
      setTimeout(()=>fetchPage(url).catch(()=>{}),Math.min(index,20)*35);
    });
  };
  if('requestIdleCallback' in window) requestIdleCallback(warmNavigation,{timeout:1800});
  else setTimeout(warmNavigation,700);

  const warmedAssets=new Set();
  const warmLinkIntent=link=>{
    const url=eligiblePageLink(link);
    if(!url) return;
    const key=url.href.split('#')[0];
    if(warmedAssets.has(key)) return;
    warmedAssets.add(key);
    fetchPage(url).then(html=>{
      const next=new DOMParser().parseFromString(html,'text/html');
      [...next.querySelectorAll('main img[src]')].slice(0,6).forEach(img=>{
        try{
          const src=new URL(img.getAttribute('src'),url.href);
          if(src.origin!==location.origin) return;
          const preload=new Image();
          preload.decoding='async';
          preload.src=src.href;
        }catch(_e){}
      });
    }).catch(()=>{});
  };
  document.addEventListener('touchstart',event=>{
    const link=event.target.closest&&event.target.closest('a');
    if(link) warmLinkIntent(link);
  },{capture:true,passive:true});
  document.addEventListener('mouseover',event=>{
    const link=event.target.closest&&event.target.closest('a');
    if(link) warmLinkIntent(link);
  },{capture:true,passive:true});

  const swipePageOrder={
    zh:['/','/about.html','/team.html','/research.html','/publications.html','/join.html','/contact.html'],
    en:['/en/','/en/about.html','/en/team.html','/en/research.html','/en/publications.html','/en/join.html','/en/contact.html']
  };

  const SWIPE_EDGE_GUARD=32;
  const SWIPE_MIN_X=58;
  const SWIPE_FLICK_MIN_X=28;
  const SWIPE_FLICK_MAX_MS=420;
  const SWIPE_FLICK_MIN_VX=.30;
  const SWIPE_MAX_MS=1200;
  const SWIPE_SETTLE_MS=330;
  const SWIPE_TEXT_SELECTION_GUARD_MS=420;
  let pageSwipeStart=null;
  let swipePreview=null;

  const hasActiveTextSelection=()=>{
    try{
      const selection=window.getSelection?.();
      return !!selection&&selection.rangeCount>0&&!selection.isCollapsed;
    }catch(_e){
      return false;
    }
  };

  const isSelectableTextTarget=target=>{
    const element=target instanceof Element?target:target?.parentElement;
    if(!element) return false;
    const text=(element.textContent||'').trim();
    if(!text) return false;
    try{
      const style=getComputedStyle(element);
      return style.userSelect!=='none'&&style.webkitUserSelect!=='none';
    }catch(_e){
      return true;
    }
  };

  const swipeBlockedTarget=target=>!!(target?.closest&&target.closest(
    '.pai-orbit,a,button,input,textarea,select,option,label,[contenteditable="true"],[role="button"],[data-no-swipe]'
  ));

  const swipeTargetFor=(path,lang,direction)=>{
    const pages=swipePageOrder[lang];
    const index=pages.indexOf(path);
    if(index<0) return null;
    return pages[(index+direction+pages.length)%pages.length];
  };

  const warmSwipeNeighbors=()=>{
    if(navigator.connection&&navigator.connection.saveData) return;
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    [-1,1].forEach(direction=>{
      const targetPath=swipeTargetFor(path,lang,direction);
      if(targetPath) fetchPage(new URL(root(targetPath),location.origin)).catch(()=>{});
    });
  };
  setTimeout(warmSwipeNeighbors,260);

  const destroySwipePreview=()=>{
    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();
    swipePreview=null;
    const main=document.querySelector('main');
    if(main){
      main.style.transform='';
      main.style.willChange='';
    }
    const footer=document.querySelector('.site-footer');
    if(footer){
      footer.style.transform='';
      footer.style.willChange='';
    }
  };

  const buildSwipePreview=(url,direction,html)=>{
    if(!pageSwipeStart||pageSwipeStart.direction!==direction) return null;
    const next=new DOMParser().parseFromString(html,'text/html');
    const nextMain=next.querySelector('main');
    const nextFooter=next.querySelector('.site-footer');
    if(!nextMain) return null;

    const shell=document.createElement('div');
    shell.setAttribute('aria-hidden','true');
    Object.assign(shell.style,{
      position:'fixed',inset:'0',overflow:'hidden',pointerEvents:'none',
      zIndex:'12',contain:'layout paint',background:'transparent'
    });
    const previewMain=document.importNode(nextMain,true);
    const previewFooter=nextFooter?document.importNode(nextFooter,true):null;
    previewMain.removeAttribute('id');
    previewMain.querySelectorAll('img[src]').forEach(img=>{
      try{ img.src=new URL(img.getAttribute('src'),url.href).href; }catch(_e){}
    });
    previewMain.querySelectorAll('source[srcset],img[srcset]').forEach(node=>{
      const raw=node.getAttribute('srcset');
      if(!raw) return;
      const resolved=raw.split(',').map(part=>{
        const bits=part.trim().split(/\s+/);
        try{ bits[0]=new URL(bits[0],url.href).href; }catch(_e){}
        return bits.join(' ');
      }).join(', ');
      node.setAttribute('srcset',resolved);
    });
    const currentMain=document.querySelector('main');
    const mainDocumentTop=Math.max(0,(currentMain?.getBoundingClientRect().top||0)+window.scrollY);
    const targetPath=normalizedPath(url.pathname);
    const targetScroll=destinationScrollForPath(targetPath);
    Object.assign(previewMain.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',
      margin:'0',willChange:'transform',pointerEvents:'none',
      background:getComputedStyle(document.body).backgroundColor||'#fff',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
    shell.appendChild(previewMain);
    if(previewFooter){
      previewFooter.removeAttribute('id');
      previewFooter.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));
      Object.assign(previewFooter.style,{
        position:'absolute',left:'0',width:'100%',margin:'0',willChange:'transform',pointerEvents:'none',
        transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
      });
      shell.appendChild(previewFooter);
    }
    document.body.appendChild(shell);
    const previewScroll=targetScroll;
    previewMain.style.top=`${mainDocumentTop-previewScroll}px`;
    if(previewFooter) previewFooter.style.top=`${mainDocumentTop+previewMain.scrollHeight-previewScroll}px`;
    swipePreview={shell,main:previewMain,footer:previewFooter,url,direction,targetScroll,previewScroll};
    return swipePreview;
  };

  const ensureSwipePreview=(direction)=>{
    const start=pageSwipeStart;
    if(!start) return Promise.resolve(null);
    if(swipePreview&&swipePreview.direction===direction) return Promise.resolve(swipePreview);
    if(swipePreview) destroySwipePreview();
    start.direction=direction;
    const targetPath=swipeTargetFor(start.path,start.lang,direction);
    if(!targetPath) return Promise.resolve(null);
    const url=new URL(root(targetPath),location.origin);
    return fetchPage(url).then(html=>buildSwipePreview(url,direction,html)).catch(()=>null);
  };

  const positionSwipePages=dx=>{
    const start=pageSwipeStart;
    if(!start) return;
    const width=Math.max(1,innerWidth);
    const bounded=Math.max(-width,Math.min(width,dx));
    const direction=bounded<0?1:-1;
    const current=document.querySelector('main');
    if(current){
      current.style.willChange='transform';
      current.style.transform=`translate3d(${bounded}px,0,0)`;
    }
    const currentFooter=document.querySelector('.site-footer');
    const footerRect=currentFooter?.getBoundingClientRect();
    const footerVisible=!!(footerRect&&footerRect.bottom>0&&footerRect.top<innerHeight);
    if(currentFooter&&footerVisible){
      currentFooter.style.willChange='transform';
      currentFooter.style.transform=`translate3d(${bounded}px,0,0)`;
    }
    const preview=swipePreview;
    if(!preview||preview.direction!==direction) return;
    const incoming=bounded+(direction>0?width:-width);
    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;
    if(preview.footer) preview.footer.style.transform=`translate3d(${incoming}px,0,0)`;
  };

  const animateElementTransform=(node,from,to,duration=SWIPE_SETTLE_MS)=>new Promise(resolve=>{
    if(!node){ resolve(); return; }
    if(matchMedia('(prefers-reduced-motion: reduce)').matches||typeof node.animate!=='function'){
      node.style.transform=to;
      resolve();
      return;
    }
    try{
      const animation=node.animate([{transform:from},{transform:to}],{
        duration,easing:'cubic-bezier(.22,.72,.22,1)',fill:'forwards'
      });
      animation.finished.then(()=>{
        node.style.transform=to;
        animation.cancel();
      }).catch(()=>{
        node.style.transform=to;
        try{ animation.cancel(); }catch(_e){}
      }).finally(resolve);
    }catch(_e){
      node.style.transform=to;
      resolve();
    }
  });

  const settleSwipeBack=async()=>{
    const current=document.querySelector('main');
    const preview=swipePreview;
    if(!current){ destroySwipePreview(); return; }
    const currentFrom=current.style.transform||'translate3d(0,0,0)';
    const currentFooter=document.querySelector('.site-footer');
    const footerFrom=currentFooter?.style.transform||'translate3d(0,0,0)';
    if(!preview){
      await Promise.all([
        animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),
        currentFooter?.style.transform?animateElementTransform(currentFooter,footerFrom,'translate3d(0,0,0)',253):Promise.resolve()
      ]);
      destroySwipePreview();
      return;
    }
    const width=Math.max(1,innerWidth);
    const incomingFrom=preview.main.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;
    const previewFooterFrom=preview.footer?.style.transform||incomingFrom;
    await Promise.all([
      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),
      currentFooter?.style.transform?animateElementTransform(currentFooter,footerFrom,'translate3d(0,0,0)',253):Promise.resolve(),
      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253),
      preview.footer?animateElementTransform(preview.footer,previewFooterFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253):Promise.resolve()
    ]);
    destroySwipePreview();
  };

  const commitSwipe=async(direction)=>{
    const current=document.querySelector('main');
    const preview=swipePreview;
    const start=pageSwipeStart;
    if(!current||!preview||!start){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=current.style.transform||'translate3d(0,0,0)';
    const currentFooter=document.querySelector('.site-footer');
    const footerFrom=currentFooter?.style.transform||'translate3d(0,0,0)';
    const incomingFrom=preview.main.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;
    const previewFooterFrom=preview.footer?.style.transform||incomingFrom;
    const targetUrl=preview.url;
    const targetScroll=Number.isFinite(preview.targetScroll)
      ?preview.targetScroll
      :destinationScrollForPath(normalizedPath(targetUrl.pathname));
    await Promise.all([
      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),
      currentFooter?.style.transform?animateElementTransform(currentFooter,footerFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330):Promise.resolve(),
      animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',330),
      preview.footer?animateElementTransform(preview.footer,previewFooterFrom,'translate3d(0,0,0)',330):Promise.resolve()
    ]);
    try{
      await applyPage(targetUrl,{transitionDirection:0,preserveScrollY:targetScroll});
    }finally{
      destroySwipePreview();
      setTimeout(warmSwipeNeighbors,60);
    }
  };

  document.addEventListener('touchstart',event=>{
    if(event.touches.length!==1||hasActiveTextSelection()){ pageSwipeStart=null; return; }
    const touch=event.touches[0];
    if(touch.clientX<=SWIPE_EDGE_GUARD||touch.clientX>=innerWidth-SWIPE_EDGE_GUARD||swipeBlockedTarget(event.target)){
      pageSwipeStart=null;
      return;
    }
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    if(!swipePageOrder[lang].includes(path)){ pageSwipeStart=null; return; }
    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang,locked:false,direction:0,lastDx:0,textCandidate:isSelectableTextTarget(event.target)};
  },{passive:true});

  document.addEventListener('touchmove',event=>{
    const start=pageSwipeStart;
    if(!start||event.touches.length!==1) return;
    const touch=event.touches[0];
    const dx=touch.clientX-start.x;
    const dy=touch.clientY-start.y;
    const ax=Math.abs(dx);
    const ay=Math.abs(dy);

    if(!start.locked){
      const held=performance.now()-start.time;
      if(hasActiveTextSelection()||(start.textCandidate&&held>=SWIPE_TEXT_SELECTION_GUARD_MS)){
        pageSwipeStart=null;
        destroySwipePreview();
        return;
      }
      if(ax<8&&ay<8) return;
      if(ay>ax*1.08){ pageSwipeStart=null; return; }
      if(ax>=8&&ax>ay*1.18) start.locked=true;
    }
    if(!start.locked) return;

    event.preventDefault();
    start.lastDx=dx;
    const direction=dx<0?1:-1;
    positionSwipePages(dx);
    if(direction!==start.direction){
      ensureSwipePreview(direction).then(()=>{
        if(pageSwipeStart===start) positionSwipePages(start.lastDx);
      });
    }
  },{passive:false});

  document.addEventListener('selectionchange',()=>{
    if(!pageSwipeStart||pageSwipeStart.locked||!hasActiveTextSelection()) return;
    pageSwipeStart=null;
    destroySwipePreview();
  });

  document.addEventListener('contextmenu',()=>{
    if(!pageSwipeStart||pageSwipeStart.locked) return;
    pageSwipeStart=null;
    destroySwipePreview();
  },{passive:true});

  document.addEventListener('touchcancel',()=>{
    const hadLocked=pageSwipeStart?.locked;
    pageSwipeStart=null;
    if(hadLocked) settleSwipeBack();
    else destroySwipePreview();
  },{passive:true});

  document.addEventListener('touchend',event=>{
    const start=pageSwipeStart;
    if(!start||!start.locked||event.changedTouches.length!==1||navigating){
      pageSwipeStart=null;
      if(start?.locked) settleSwipeBack();
      else destroySwipePreview();
      return;
    }
    const touch=event.changedTouches[0];
    const dx=touch.clientX-start.x;
    const dy=touch.clientY-start.y;
    const elapsed=Math.max(1,performance.now()-start.time);
    const vx=dx/elapsed;
    const horizontal=Math.abs(dx)>=Math.abs(dy)*1.15;
    const distanceCommit=Math.abs(dx)>=SWIPE_MIN_X;
    const flickCommit=Math.abs(dx)>=SWIPE_FLICK_MIN_X&&elapsed<=SWIPE_FLICK_MAX_MS&&Math.abs(vx)>=SWIPE_FLICK_MIN_VX;
    const direction=dx<0?1:-1;

    if(elapsed>SWIPE_MAX_MS||!horizontal||(!distanceCommit&&!flickCommit)||!swipePreview||swipePreview.direction!==direction){
      pageSwipeStart=null;
      settleSwipeBack();
      return;
    }

    const current=normalizedPath();
    if(current!==start.path){
      pageSwipeStart=null;
      settleSwipeBack();
      return;
    }
    event.preventDefault();
    saveCurrentScroll();
    cacheCurrentPageSnapshot();
    commitSwipe(direction).finally(()=>{ pageSwipeStart=null; });
  },{passive:false});

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
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'
  }[char]));
  const doiHref=doi=>'https://doi.org/'+String(doi).trim().split('/').map(encodeURIComponent).join('/');
  const getExpandedYears=()=>[...document.querySelectorAll('.pub-group[data-expanded="true"]')]
    .map(element=>element.dataset.year).filter(Boolean);

  const publicationLanguage=()=>((document.documentElement.lang||'').toLowerCase().startsWith('en')?'en':'zh');
  const yearToggleLabel=(open,count,en)=>open?(en?'Show less ↑':'收起 ↑'):(en?`View all ${count} ↓`:`展开全部 ${count} 篇 ↓`);

  const setYearExpanded=(section,open)=>{
    if(!section) return;
    section.dataset.expanded=open?'true':'false';
    section.querySelectorAll('.pub[data-pub-extra="1"]').forEach(article=>article.classList.toggle('is-collapsed',!open));
    const toggle=section.querySelector('[data-pub-toggle]');
    if(toggle){
      const count=section.querySelectorAll('.pub').length;
      const en=publicationLanguage()==='en';
      toggle.setAttribute('aria-expanded',open?'true':'false');
      toggle.textContent=yearToggleLabel(open,count,en);
    }
  };

  const syncAllPublicationToggle=()=>{
    const button=document.querySelector('[data-pub-toggle-all]');
    if(!button) return;
    const groups=[...document.querySelectorAll('.pub-group')].filter(section=>section.querySelector('[data-pub-toggle]'));
    const allOpen=groups.length>0&&groups.every(section=>section.dataset.expanded==='true');
    const en=publicationLanguage()==='en';
    button.dataset.open=allOpen?'true':'false';
    button.setAttribute('aria-expanded',allOpen?'true':'false');
    button.textContent=allOpen?(en?'Collapse':'收起'):(en?'All':'全部');
  };

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
      const en=publicationLanguage()==='en';
      const expanded=new Set((expandedYears||[]).map(String));
      const fragment=document.createDocumentFragment();
      const years=[...byYear.keys()];

      const toolbar=document.createElement('div');
      toolbar.className='publication-toolbar';

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
      if([...byYear.values()].some(pubs=>pubs.length>PUB_VISIBLE_DEFAULT)){
        const allToggle=document.createElement('button');
        allToggle.type='button';
        allToggle.className='publication-year-link pub-toggle-all';
        allToggle.dataset.pubToggleAll='1';
        yearNav.appendChild(allToggle);
      }
      toolbar.appendChild(yearNav);
      fragment.appendChild(toolbar);

      for(const [year,pubs] of byYear){
        const section=document.createElement('section');
        section.className='pub-group';
        section.id=`pub-year-${year}`;
        section.dataset.year=String(year);
        const isExpanded=expanded.has(String(year));
        section.dataset.expanded=isExpanded?'true':'false';
        const count=en?`${pubs.length} publication${pubs.length===1?'':'s'}`:`${pubs.length} 篇论文`;
        section.innerHTML=`<div class="pub-year-row"><h2 class="pub-year">${year}</h2><span>${count}</span></div>`;

        pubs.forEach((publication,index)=>{
          const article=document.createElement('article');
          const extra=index>=PUB_VISIBLE_DEFAULT;
          article.className='pub'+(!isExpanded&&extra?' is-collapsed':'');
          article.dataset.pubExtra=extra?'1':'0';
          const actions=publication.doi?
            `<div class="pub-actions"><a href="${esc(doiHref(publication.doi))}" target="_blank" rel="noopener">DOI ↗</a></div>`:'';
          article.innerHTML=`<h3 class="title-item">${esc(publication.title)}</h3><p class="pub-authors">${esc(publication.authors)}</p><p class="pub-venue">${esc(publication.venue)} · ${year}</p>${actions}`;
          section.appendChild(article);
        });

        if(pubs.length>PUB_VISIBLE_DEFAULT){
          const toggle=document.createElement('button');
          toggle.type='button';
          toggle.className='pub-toggle';
          toggle.dataset.pubToggle=String(year);
          toggle.setAttribute('aria-expanded',isExpanded?'true':'false');
          toggle.textContent=yearToggleLabel(isExpanded,pubs.length,en);
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
      syncAllPublicationToggle();
      updateBackTopVisibility();
    }catch(_e){
      const en=publicationLanguage()==='en';
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

    const allToggle=event.target.closest&&event.target.closest('[data-pub-toggle-all]');
    if(allToggle){
      event.preventDefault();
      const open=allToggle.dataset.open!=='true';
      document.querySelectorAll('.pub-group').forEach(section=>{
        if(section.querySelector('[data-pub-toggle]')) setYearExpanded(section,open);
      });
      syncAllPublicationToggle();
      return;
    }

    const toggle=event.target.closest&&event.target.closest('[data-pub-toggle]');
    if(toggle){
      event.preventDefault();
      const section=toggle.closest('.pub-group');
      if(!section) return;
      setYearExpanded(section,section.dataset.expanded!=='true');
      syncAllPublicationToggle();
      return;
    }

    const top=document.querySelector('[data-pub-back-top]');
    if(top){
      event.preventDefault();
      window.scrollTo({top:0,behavior:'smooth'});
    }
  },true);

  initPublications([]);
  siteReady.catch(()=>{});

  const initOrbitMenu=()=>{
    if(document.querySelector('.pai-orbit')) return;
    const orbit=document.createElement('div');
    orbit.className='pai-orbit';
    orbit.innerHTML='<div class="pai-orbit-backdrop" aria-hidden="true"></div><div class="pai-orbit-wheel" role="navigation"></div><button class="pai-orbit-toggle" type="button" aria-expanded="false"><span aria-hidden="true"></span></button>';
    document.body.appendChild(orbit);

    const wheel=orbit.querySelector('.pai-orbit-wheel');
    const toggle=orbit.querySelector('.pai-orbit-toggle');
    const backdrop=orbit.querySelector('.pai-orbit-backdrop');
    let rotation=0;
    let dragging=false;
    let moved=false;
    let startAngle=0;
    let startRotation=0;
    let autoRaf=0;
    let autoLastTs=0;
    let autoTimer=0;
    const AUTO_DEG_PER_SECOND=6;

    const menuData=()=>{
      const en=normalizedPath().startsWith('/en/');
      const lang=en?'en':'zh';
      const languageLabel=en?'中文':'EN';
      const home=[en?'Home':'首页',en?'/en/':'/'];
      return [home,...navItems(lang),[languageLabel,counterpartWithContext(normalizedPath())]];
    };

    const sync=()=>{
      const en=normalizedPath().startsWith('/en/');
      const data=menuData();
      const markup=[];
      const layout=data.map(([label,href])=>{
        const chars=Array.from(label);
        const ascii=chars.every(ch=>/[\x00-\x7F]/.test(ch));
        const charStep=ascii?4.8:7.6;
        const glyphSpan=ascii?4.6:6.4;
        const span=(Math.max(0,chars.length-1)*charStep)+glyphSpan;
        return {label,href,chars,charStep,span,center:0};
      });
      const used=layout.reduce((sum,item)=>sum+item.span,0);
      const gap=Math.max(0,(360-used)/layout.length);
      for(let i=1;i<layout.length;i++){
        const prev=layout[i-1];
        const item=layout[i];
        item.center=prev.center+prev.span/2+gap+item.span/2;
      }
      layout.forEach(({label,href,chars,charStep,center})=>{
        markup.push(`<a class="pai-orbit-item" aria-label="${label}" href="${root(href)}" style="--item-angle:${center}deg"><span class="pai-orbit-sr">${label}</span></a>`);
        chars.forEach((ch,j)=>{
          const offset=(j-(chars.length-1)/2)*charStep;
          markup.push(`<span class="pai-orbit-char" aria-hidden="true" style="--char-angle:${center+offset}deg">${ch}</span>`);
        });
      });
      wheel.innerHTML=markup.join('');
      wheel.setAttribute('aria-label',en?'Quick navigation':'快捷导航');
      toggle.setAttribute('aria-label',orbit.classList.contains('open')?(en?'Close quick menu':'关闭快捷菜单'):(en?'Open quick menu':'打开快捷菜单'));
    };

    const paint=()=>wheel.style.setProperty('--orbit-rotation',rotation+'deg');
    const stopAuto=()=>{
      if(autoTimer){clearTimeout(autoTimer);autoTimer=0;}
      if(autoRaf){cancelAnimationFrame(autoRaf);autoRaf=0;}
      autoLastTs=0;
      orbit.classList.remove('auto-rotating');
    };
    const autoTick=ts=>{
      if(!orbit.classList.contains('open')||dragging){stopAuto();return;}
      if(autoLastTs){
        const dt=Math.min(50,ts-autoLastTs);
        rotation+=AUTO_DEG_PER_SECOND*dt/1000;
        paint();
      }
      autoLastTs=ts;
      autoRaf=requestAnimationFrame(autoTick);
    };
    const startAuto=()=>{
      if(autoRaf||dragging||!orbit.classList.contains('open')) return;
      orbit.classList.add('auto-rotating');
      autoLastTs=0;
      autoRaf=requestAnimationFrame(autoTick);
    };
    const scheduleAuto=(delay=100)=>{
      if(autoTimer) clearTimeout(autoTimer);
      autoTimer=setTimeout(()=>{autoTimer=0;startAuto();},delay);
    };
    const pointAngle=e=>{
      const rect=wheel.getBoundingClientRect();
      const p=e.touches?e.touches[0]:e;
      return Math.atan2(p.clientY-(rect.top+rect.height/2),p.clientX-(rect.left+rect.width/2))*180/Math.PI;
    };
    const setOpen=open=>{
      if(!open) stopAuto();
      orbit.classList.toggle('open',open);
      toggle.setAttribute('aria-expanded',open?'true':'false');
      if(open){
        sync();
        scheduleAuto(560);
      }
      toggle.setAttribute('aria-label',open?(normalizedPath().startsWith('/en/')?'Close quick menu':'关闭快捷菜单'):(normalizedPath().startsWith('/en/')?'Open quick menu':'打开快捷菜单'));
    };
    const begin=e=>{
      if(!orbit.classList.contains('open')) return;
      stopAuto();
      dragging=true;
      moved=false;
      orbit.classList.add('dragging');
      startAngle=pointAngle(e);
      startRotation=rotation;
      if(e.pointerId!==undefined) wheel.setPointerCapture?.(e.pointerId);
    };
    const move=e=>{
      if(!dragging) return;
      const delta=pointAngle(e)-startAngle;
      if(Math.abs(delta)>3) moved=true;
      rotation=startRotation+delta;
      paint();
    };
    const end=()=>{ dragging=false; orbit.classList.remove('dragging'); scheduleAuto(120); };

    toggle.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();setOpen(!orbit.classList.contains('open'));});

    if(window.PointerEvent){
      wheel.addEventListener('pointerdown',e=>{e.stopPropagation();begin(e);});
      wheel.addEventListener('pointermove',e=>{if(dragging)e.preventDefault();e.stopPropagation();move(e);});
      wheel.addEventListener('pointerup',e=>{e.stopPropagation();end();});
      wheel.addEventListener('pointercancel',end);
    }else{
      wheel.addEventListener('touchstart',e=>{if(e.touches.length===1){e.stopPropagation();begin(e);}},{passive:true});
      wheel.addEventListener('touchmove',e=>{if(dragging&&e.touches.length===1){e.preventDefault();e.stopPropagation();move(e);}},{passive:false});
      wheel.addEventListener('touchend',e=>{e.stopPropagation();end();},{passive:true});
      wheel.addEventListener('touchcancel',end,{passive:true});
    }

    wheel.addEventListener('click',e=>{
      const link=e.target.closest&&e.target.closest('a');
      if(!link) return;
      if(moved){
        e.preventDefault();
        e.stopPropagation();
        moved=false;
        return;
      }
    },true);

    new MutationObserver(()=>{if(orbit.classList.contains('open'))sync();}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    sync();
    paint();
  };
  initOrbitMenu();

})();
