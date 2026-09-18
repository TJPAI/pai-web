const CACHE='pai-site-v20260918-7';
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

self.addEventListener('install',event=>{
  event.waitUntil(
    caches.open(CACHE)
      .then(cache=>cache.addAll(CORE))
      .then(()=>self.skipWaiting())
  );
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
      if(response&&response.ok) await cache.put(request,response.clone());
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
