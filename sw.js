const CACHE='pai-site-v20260918-9';
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

const HOME_RESEARCH_STYLE=`<style id="pai-home-research-mobile">@media(max-width:768px){
.research-grid .research .research-code{display:grid;grid-template-columns:auto auto minmax(0,1fr);align-items:center;column-gap:10px;row-gap:0;margin-bottom:22px;line-height:1}
.research-grid .research .research-code-main{display:contents}
.research-grid .research .research-index{font-size:16px!important;line-height:1.05!important;letter-spacing:.08em!important;font-weight:500!important;color:#A8AFB9!important;white-space:nowrap}
.research-grid .research .research-code-main>span{font-size:17px;line-height:1.05;letter-spacing:.09em;font-weight:700;color:var(--ink);white-space:nowrap}
.research-grid .research .research-expansion{font-size:9px;line-height:1.12;letter-spacing:.055em;font-weight:500;text-transform:uppercase;color:var(--muted);white-space:normal;text-wrap:balance;display:block;max-width:none}
.research-grid .research:nth-child(1) .research-expansion{width:112px}
.research-grid .research:nth-child(2) .research-expansion{width:146px}
.research-grid .research:nth-child(3) .research-expansion{width:166px}
}</style>`;

const decorateHtml=async response=>{
  if(!response) return response;
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html')) return response;
  const text=await response.text();
  if(text.includes('id="pai-home-research-mobile"')) return new Response(text,{status:response.status,statusText:response.statusText,headers:response.headers});
  const decorated=text.replace('<main>','<main>'+HOME_RESEARCH_STYLE);
  return new Response(decorated,{status:response.status,statusText:response.statusText,headers:response.headers});
};

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
    if(cached) return decorateHtml(cached);

    try{
      const response=await fetch(request);
      if(response&&response.ok) await cache.put(request,response.clone());
      return decorateHtml(response);
    }catch(_e){
      if(request.mode==='navigate'){
        const fallback=await cache.match('./index.html');
        if(fallback) return decorateHtml(fallback);
      }
      return new Response('Offline',{status:503,statusText:'Offline'});
    }
  })());
});
