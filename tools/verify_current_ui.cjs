const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium,webkit}=require('playwright');
const engine=process.env.PAI_BROWSER==='webkit'?webkit:chromium;
const BASE='https://tjpai.github.io/pai-web/',ROOT=path.resolve(__dirname,'..');
(async()=>{
 const browser=await engine.launch({headless:true,...(engine===chromium?{args:['--no-sandbox']}:{})});
 try{
  for(const width of [390,1280]){
   const ctx=await browser.newContext({viewport:{width,height:844},locale:'zh-CN',isMobile:width===390,hasTouch:width===390});
   await ctx.route(BASE+'**',route=>{
    const u=new URL(route.request().url());let name=decodeURIComponent(u.pathname.slice('/pai-web/'.length));if(!name||name.endsWith('/'))name+='index.html';
    const file=path.resolve(ROOT,name);
    if(!file.startsWith(ROOT+path.sep)||!fs.existsSync(file))return route.fulfill({status:404,body:name});
    const ext=path.extname(file).toLowerCase(),mime={'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.webp':'image/webp'}[ext]||'application/octet-stream';
    return route.fulfill({status:200,body:fs.readFileSync(file),contentType:mime});
   });
   const p=await ctx.newPage(),errs=[];p.on('pageerror',e=>errs.push(e.message));
   for(const [lang,label,word] of [['','（最新动态）','更多'],['en/','(latest updates)','More']]){
    await p.goto(BASE+lang+'index.html');
    await p.locator('.site-header .nav-links a[href$="publications.html"] .nav-updates-hint').waitFor({state:'attached'});
    assert.equal((await p.locator('.site-header .nav-links .nav-updates-hint').first().textContent()).trim(),label);
    const first=p.locator('.site-header .nav-links a[href$="publications.html"]');
    assert.equal(await first.locator('.nav-updates-hint').evaluate(e=>getComputedStyle(e).color),'rgb(188, 37, 48)');
    await p.goto(BASE+lang+'publications.html');
    await p.locator('.results-news-toggle').waitFor();
    assert.equal(await p.locator('.results-news-list:not(.results-news-extra) .results-news-row').count(),5);
    assert.equal(await p.locator('.results-news-extra .results-news-row').count(),40);
    assert.equal(await p.locator('.results-news-extra').isVisible(),false);
    await p.locator('.results-news-toggle').click();
    assert.equal(await p.locator('.results-news-extra').isVisible(),true);
    assert.equal(await p.locator('.results-news-toggle').getAttribute('aria-expanded'),'true');
    await p.locator('.results-news-toggle').click();
    assert.equal(await p.locator('.results-news-extra').isVisible(),false);
    assert.equal(await p.locator('.results-news-toggle').getAttribute('aria-expanded'),'false');
    assert.equal(await p.locator('.site-header .nav-links .nav-updates-hint').first().textContent(),label);
    const overflow=await p.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
    assert.ok(overflow<=2,'horizontal overflow: '+overflow+' '+width+' '+lang);
   }
   // Real navigation: internal link, Back/Forward and homepage research CTA.
   for(const lang of ['', 'en/']){
     await p.goto(BASE+lang+'index.html');
     const cta=p.locator('.home-achievements-more a');
     await cta.scrollIntoViewIfNeeded();
     await cta.click();
     await p.waitForURL(BASE+lang+'publications.html');
     await p.locator('.results-news-toggle').waitFor();
     await p.goBack();
     await p.waitForURL(BASE+lang+'index.html');
     await p.goForward();
     await p.waitForURL(BASE+lang+'publications.html');
     await p.locator('.results-news-toggle').waitFor();
     if(width===390){
       const menu=p.locator('.menu-btn');
       await menu.click();
       assert.equal(await menu.getAttribute('aria-expanded'),'true');
       assert.equal(await p.locator('.mobile-menu.open').count(),1);
       await menu.click();
       assert.equal(await menu.getAttribute('aria-expanded'),'false');
       const orbit=p.locator('.pai-orbit-toggle');
       if(await orbit.count()){
         await orbit.click();
         await p.waitForTimeout(160);
         await menu.click();
         assert.equal(await p.locator('.pai-orbit.open').count(),0);
         assert.equal(await orbit.getAttribute('aria-expanded'),'false');
         await menu.click();
       }
     }
   }
   assert.deepEqual(errs,[]);
   console.log('PASS',process.env.PAI_BROWSER||'chromium',width,'both languages: menu hint + color, news 5/45 expand/collapse, overflow, no JS exceptions');
   await ctx.close();
  }
 } finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
