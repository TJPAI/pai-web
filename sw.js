const CACHE='pai-site-v20260918-12';
const CORE=[
  './','./index.html','./about.html','./research.html','./team.html','./publications.html','./join.html','./contact.html',
  './en/','./en/index.html','./en/about.html','./en/research.html','./en/team.html','./en/publications.html','./en/join.html','./en/contact.html',
  './people/erwu-liu.html','./people/rui-wang.html','./people/gang-shen.html','./people/dunhui-xiao.html','./people/shuyan-hu.html','./people/yan-liu.html',
  './en/people/erwu-liu.html','./en/people/rui-wang.html','./en/people/gang-shen.html','./en/people/dunhui-xiao.html','./en/people/shuyan-hu.html','./en/people/yan-liu.html',
  './assets/css/site.css','./assets/css/refine.css','./assets/css/team.css',
  './assets/js/site.js','./assets/js/publications.js','./assets/js/publications-en.js',
  './data/publications.json','./data/publications-archive.json',
  './assets/images/people/erwu-liu.jpg','./assets/images/people/rui-wang.jpg','./assets/images/people/gang-shen.jpg','./assets/images/people/dunhui-xiao.jpg','./assets/images/people/shuyan-hu.jpg','./assets/images/people/yan-liu.jpg'
];

const SHARED_UI_STYLE=`<style id="pai-home-research-mobile">@media(max-width:768px){
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
}</style>`;

const decorateHtml=async response=>{
  if(!response) return response;
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html')) return response;
  const text=await response.text();
  if(text.includes('id="pai-home-research-mobile"')) return new Response(text,{status:response.status,statusText:response.statusText,headers:response.headers});
  const decorated=text.replace('<main>','<main>'+SHARED_UI_STYLE);
  return new Response(decorated,{status:response.status,statusText:response.statusText,headers:response.headers});
};

const precache=async()=>{
  const cache=await caches.open(CACHE);
  await Promise.all(CORE.map(async path=>{
    const request=new Request(path,{cache:'reload'});
    const response=await fetch(request);
    if(!response.ok) throw new Error(`precache failed: ${path}`);
    await cache.put(request,await decorateHtml(response));
  }));
};

self.addEventListener('install',event=>{
  event.waitUntil(precache().then(()=>self.skipWaiting()));
});

self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener('message',event=>{
  if(event.data&&event.data.type==='SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch',event=>{
  const request=event.request;
  if(request.method!=='GET') return;
  const url=new URL(request.url);
  if(url.origin!==self.location.origin) return;

  event.respondWith((async()=>{
    const cache=await caches.open(CACHE);
    const cached=await cache.match(request,{ignoreSearch:true});
    if(cached) return cached;

    try{
      const response=await fetch(request);
      if(response&&response.ok){
        const stored=await decorateHtml(response.clone());
        await cache.put(request,stored.clone());
        return stored;
      }
      return response;
    }catch(_e){
      if(request.mode==='navigate'){
        const fallback=await cache.match('./index.html');
        if(fallback) return fallback;
      }
      return new Response('Offline',{status:503,statusText:'Offline'});
    }
  })());
});
