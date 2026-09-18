const CACHE='pai-site-v20260918-34';
const CORE=[
  './','./index.html','./about.html','./research.html','./team.html','./publications.html','./join.html','./contact.html','./news.html',
  './en/','./en/index.html','./en/about.html','./en/research.html','./en/team.html','./en/publications.html','./en/join.html','./en/contact.html',
  './people/erwu-liu.html','./people/rui-wang.html','./people/gang-shen.html','./people/dunhui-xiao.html','./people/shuyan-hu.html','./people/yan-liu.html',
  './en/people/erwu-liu.html','./en/people/rui-wang.html','./en/people/gang-shen.html','./en/people/dunhui-xiao.html','./en/people/shuyan-hu.html','./en/people/yan-liu.html',
  './assets/css/site.css','./assets/css/refine.css','./assets/css/refine-base.css','./assets/css/app-core.css','./assets/css/app.css','./assets/css/team.css','./assets/js/site.js',
  './data/publications.json','./data/publications-archive.json',
  './assets/images/people/erwu-liu.jpg','./assets/images/people/rui-wang.jpg','./assets/images/people/gang-shen.jpg','./assets/images/people/dunhui-xiao.jpg','./assets/images/people/shuyan-hu.jpg','./assets/images/people/yan-liu.jpg'
];

const precache=async()=>{
  const cache=await caches.open(CACHE);
  await Promise.all(CORE.map(async path=>{
    try{
      const request=new Request(path,{cache:'reload'});
      const response=await fetch(request);
      if(response.ok) await cache.put(request,response.clone());
    }catch(_e){}
  }));
};

/* Do not call skipWaiting here. A new bundle waits until the current browsing
   session is finished, preventing old JS from running against new HTML/CSS. */
self.addEventListener('install',event=>{
  event.waitUntil(precache());
});

self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(key=>key.startsWith('pai-site-')&&key!==CACHE).map(key=>caches.delete(key))))
      .then(()=>self.clients.claim())
  );
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
      if(response&&response.ok) await cache.put(request,response.clone());
      return response;
    }catch(_e){
      if(request.mode==='navigate'){
        const english=/\/en(?:\/|$)/.test(url.pathname);
        const fallback=await cache.match(english?'./en/index.html':'./index.html');
        if(fallback) return fallback;
      }
      return new Response('Offline',{status:503,statusText:'Offline'});
    }
  })());
});
