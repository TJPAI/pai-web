/* Controlled latency check, not a claim about live-site network speed.
   Optional PAI_SITE_JS_OVERRIDE lets the same scenario measure an earlier runtime. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..'),BASE='https://tjpai.github.io/pai-web/';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.PAI_BROWSER_EXECUTABLE||undefined,args:['--disable-dev-shm-usage','--disable-gpu']});
 try{
  const context=await browser.newContext({viewport:{width:390,height:844},locale:'zh-CN'});
  const counts={};let firstData=null,failContactOnce=false;const delay=600;
  await context.route(BASE+'**',async route=>{
   let file=new URL(route.request().url()).pathname.slice('/pai-web/'.length);if(!file||file.endsWith('/'))file+='index.html';
   counts[file]=(counts[file]||0)+1;
   if(file.startsWith('data/'))firstData??=Date.now();
   if(file.endsWith('.html')||file.endsWith('.json'))await new Promise(r=>setTimeout(r,delay));
   if(file==='contact.html'&&failContactOnce){failContactOnce=false;return route.fulfill({status:503,body:'Temporary test failure'});}
   const source=file==='assets/js/site.js'&&process.env.PAI_SITE_JS_OVERRIDE?process.env.PAI_SITE_JS_OVERRIDE:path.join(ROOT,file);
   const contentType=({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp'})[path.extname(file)];
   await route.fulfill({status:fs.existsSync(source)?200:404,body:fs.existsSync(source)?fs.readFileSync(source):'missing',contentType});
  });
  const page=await context.newPage();await page.goto(BASE+'research.html');
  await page.waitForTimeout(120);
  await page.locator('.site-footer a[href="/pai-web/publications.html"]').evaluate(a=>a.dispatchEvent(new MouseEvent('mouseover',{bubbles:true})));
  await page.waitForTimeout(200);
  const clicked=Date.now();
  await page.locator('.site-footer a[href="/pai-web/publications.html"]').evaluate(a=>{
   const started=performance.now();
   const observer=new MutationObserver(()=>{
    if(document.querySelector('.pub')){window.__paperWait=performance.now()-started;observer.disconnect();}
   });
   observer.observe(document.body,{childList:true,subtree:true});a.click();
  });
  await page.locator('.pub').first().waitFor();const elapsed=await page.evaluate(()=>Math.round(window.__paperWait));
  const result={simulated_request_latency_ms:delay,publications_html_requests:counts['publications.html'],paper_data_started_before_click:firstData<clicked,click_to_papers_ms:elapsed,total_html_requests:Object.entries(counts).filter(([k])=>k.endsWith('.html')).reduce((n,[,v])=>n+v,0)};
  console.log(JSON.stringify(result));
  if(!process.env.PAI_SITE_JS_OVERRIDE){
   assert.equal(result.publications_html_requests,1,'Page prefetch and click did not share a request');
   assert.ok(result.paper_data_started_before_click,'Paper data was not prefetched on intent');
   assert.equal(counts['data/publications.json'],1);assert.equal(counts['data/publications-archive.json'],1);
   failContactOnce=true;
   const contact=page.locator('.site-footer a[href="/pai-web/contact.html"]');
   await Promise.all([
    page.waitForResponse(r=>r.url()===BASE+'contact.html'&&r.status()===503),
    contact.evaluate(a=>a.dispatchEvent(new MouseEvent('mouseover',{bubbles:true})))
   ]);
   await page.waitForTimeout(50);
   await contact.evaluate(a=>{a.dispatchEvent(new MouseEvent('mouseover',{bubbles:true}));a.click();});
   await page.waitForURL(BASE+'contact.html');await page.locator('.contact-grid').waitFor();
   assert.equal(counts['contact.html'],2,'Failed prefetch was retained or retry duplicated requests');
   console.log('Failed page prefetch retried successfully; hover and click shared the retry.');
  }
  await context.close();
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
