// Isolated browser regression: catch dropped popstate and sync prefetch exceptions.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium,webkit}=require('playwright');
const engine=process.env.PAI_BROWSER==='webkit'?webkit:chromium;
const BASE='https://tjpai.github.io/pai-web/',ROOT=path.resolve(__dirname,'..');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await engine.launch({headless:true,...(engine===chromium?{args:['--no-sandbox']}:{})});
 try{
  const ctx=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,locale:'zh-CN'});
  await ctx.route(BASE+'**',route=>{
   const u=new URL(route.request().url());let name=decodeURIComponent(u.pathname.slice('/pai-web/'.length));
   if(!name||name.endsWith('/'))name+='index.html';
   const file=path.resolve(ROOT,name);
   if(!file.startsWith(ROOT+path.sep)||!fs.existsSync(file))return route.fulfill({status:404,body:name});
   const type={'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.webp':'image/webp'}[path.extname(file)]||'application/octet-stream';
   return route.fulfill({status:200,body:fs.readFileSync(file),contentType:type});
  });
  const p=await ctx.newPage(),errors=[];
  p.on('pageerror',e=>errors.push(e.message));
  await p.goto(BASE+'about.html');
  await p.evaluate(()=>{localStorage.setItem('pai-lang','zh');});
  const click=async href=>p.locator('.site-footer a[href="'+href+'"]').first().evaluate(a=>a.click());
  const consistent=async(expected)=>{
   await p.waitForFunction(target=>{
    const u=new URL(location.href);
    const footer=document.querySelector('.site-footer');
    return u.pathname==='/pai-web/'+target &&
     document.querySelector('main')?.querySelector('h1')?.textContent?.trim().length>0 &&
     document.querySelector('main')?.style.transform==='' &&
     footer!=null &&
     document.title.length>0;
   },expected,{timeout:10000});
  };
  // Exercise back and forward while an SPA transition is still active.
  for(let k=0;k<8;k++){
   await p.goto(BASE+'about.html');
   await p.evaluate(()=>scrollTo(0,600));await sleep(200);
   await click('research.html');
   await p.waitForURL(BASE+'research.html');
   await sleep(450);
   await p.evaluate(()=>scrollTo(0,350));await sleep(200);
   await p.goBack();await p.waitForURL(BASE+'about.html');
   await p.goForward();await p.waitForURL(BASE+'research.html');
   await consistent('research.html');
   await sleep(450);
   const state=await p.evaluate(()=>({url:location.pathname,scrollY:Math.round(scrollY),saved:history.state?.scrollY||0,title:document.title,main:document.querySelector('main h1')?.textContent?.trim()||''}));
   assert.equal(state.url,'/pai-web/research.html');
   assert.ok(Math.abs(state.scrollY-350)<=2,'research scroll restoration '+JSON.stringify(state));
   assert.ok(Math.abs(state.saved-350)<=2,'history scroll mismatch '+JSON.stringify(state));
   console.log('PASS burst-history iteration',k+1);
  }
  // Inject synchronous fetch exception only for HTML warm requests after page load.
  await p.goto(BASE+'about.html');
  await p.evaluate(()=>{
   const original=window.fetch.bind(window);
   window.fetch=(input,opts)=>{if(String(input).includes('/contact.html'))throw new TypeError('QA_SYNC_FETCH_INJECTED');return original(input,opts)};
  });
  await sleep(900);
  assert.deepEqual(errors,[],'uncaught page errors: '+errors.join(' | '));
  console.log('PASS no uncaught page errors; engine='+ (process.env.PAI_BROWSER||'chromium'));
  await ctx.close();
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
