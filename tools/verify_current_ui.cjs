const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium,webkit}=require('playwright');
const engine=process.env.PAI_BROWSER==='webkit'?webkit:chromium;
const BASE='https://tjpai.github.io/pai-web/',ROOT=path.resolve(__dirname,'..');
const news=JSON.parse(fs.readFileSync(path.join(ROOT,'data/latest-news.json'),'utf8'));
const newsDefaultVisible=news.default_visible,newsExpandedCount=news.items.length-newsDefaultVisible;
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
    const toggle=p.locator('.results-news-toggle');
    await toggle.waitFor();
    assert.equal(await toggle.evaluate(e=>e.parentElement.lastElementChild===e),true);
    assert.equal(await toggle.textContent(),'');
    assert.equal(await toggle.locator('svg').count(),1);
    assert.equal(await toggle.getAttribute('aria-label'),lang?'Expand latest news':'展开最新动态');
    assert.equal(await toggle.locator('svg').evaluate(e=>getComputedStyle(e).transform),'none');
    assert.ok((await toggle.boundingBox()).height>=44);
    assert.equal(await p.locator('.results-news-list:not(.results-news-extra) .results-news-row').count(),newsDefaultVisible);
    assert.equal(await p.locator('.results-news-extra .results-news-row').count(),newsExpandedCount);
    assert.equal(await p.locator('.results-news-extra').isVisible(),false);
    await p.locator('.results-news-toggle').click();
    assert.equal(await p.locator('.results-news-extra').isVisible(),true);
    assert.equal(await toggle.getAttribute('aria-expanded'),'true');
    assert.equal(await toggle.getAttribute('aria-label'),lang?'Collapse latest news':'收起最新动态');
    assert.notEqual(await toggle.locator('svg').evaluate(e=>getComputedStyle(e).transform),'none');
    await p.locator('.results-news-toggle').click();
    assert.equal(await p.locator('.results-news-extra').isVisible(),false);
    assert.equal(await toggle.getAttribute('aria-expanded'),'false');
    await p.waitForFunction(()=>{const b=document.querySelector('.results-news-toggle').getBoundingClientRect();const h=document.querySelector('.site-header').getBoundingClientRect();return b.top>=h.bottom&&b.bottom<=innerHeight;});
    assert.equal(await toggle.locator('svg').evaluate(e=>getComputedStyle(e).transform),'none');
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
   // Contact phone reveal: direct entry and lightweight navigation, both languages.
   for(const lang of ['', 'en/']){
     await p.goto(BASE+lang+'contact.html');
     const page=p.locator('.page-contact');
     const buttons=page.locator('button[data-contact-phone]');
     assert.equal(await buttons.count(),2);
     assert.equal(await page.locator('a[href^="tel:"]').count(),0);
     for(const key of ['cooperation','recruitment']){
       const card=page.locator('#'+key);
       const button=card.locator('button[data-contact-phone]');
       const digits=(key==='cooperation'?['159','2179','7370']:['195','3699','0671']).join('');
       if(width===390) await button.tap(); else {await button.focus();await button.press('Enter');}
       const link=card.locator('a[href^="tel:"]');
       await link.waitFor();
       assert.equal(await link.getAttribute('href'),'tel:+86'+digits);
       assert.equal((await link.textContent()).replace(/\s/g,''),(lang?'+86':'')+digits);
       assert.equal(await button.count(),0);
     }
     await p.goto(BASE+lang+'join.html');
     const cta=p.locator('main a[href$="contact.html#recruitment"]').first();
     await cta.click();
     await p.waitForURL(BASE+lang+'contact.html#recruitment');
     const recruit=p.locator('#recruitment button[data-contact-phone]');
     await recruit.click();
     assert.equal(await p.locator('#recruitment a[href^="tel:"]').count(),1);
     assert.equal(await p.locator('#cooperation a[href^="tel:"]').count(),0);
   }
   assert.deepEqual(errs,[]);
   console.log('PASS',width,'both languages: menu hint + color, news '+newsDefaultVisible+'/'+newsExpandedCount+' expand/collapse, overflow, no JS exceptions');
   await ctx.close();
  }
 } finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
