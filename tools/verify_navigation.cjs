/* Browser regression checks. Run with Playwright installed; optionally set
   PAI_BROWSER_EXECUTABLE to use an existing Chromium binary. No live writes. */
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const BASE='https://tjpai.github.io/pai-web/';
const files=['index.html','about.html','team.html','research.html','publications.html','join.html','contact.html',
  ...['erwu-liu','rui-wang','gang-shen','dunhui-xiao','shuyan-hu','yan-liu'].map(n=>`people/${n}.html`)];
const headSelector='meta[name="description"],meta[property^="og:"],meta[name^="twitter:"],link[rel="canonical"],link[rel="alternate"][hreflang],script[type="application/ld+json"][data-pai-schema]';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.env.PAI_BROWSER_EXECUTABLE||undefined,args:['--disable-dev-shm-usage','--disable-gpu']});
  let failures=[];
  try{
    for(const width of [390,1280]){
      const context=await browser.newContext({viewport:{width,height:844},locale:'zh-CN',hasTouch:width===390,isMobile:width===390});
      let failPapers=false,slowImages=false;
      await context.route(BASE+'**',async route=>{
        const url=new URL(route.request().url());
        let name=decodeURIComponent(url.pathname.slice('/pai-web/'.length));
        if(!name||name.endsWith('/'))name+='index.html';
        if(failPapers&&name.startsWith('data/publications'))return route.abort();
        if(slowImages&&name.startsWith('assets/images/home/'))await sleep(150);
        const file=path.resolve(ROOT,name);
        if(!file.startsWith(ROOT+path.sep)||!fs.existsSync(file)){
          failures.push(`Missing local resource: ${name}`);return route.fulfill({status:404,body:'Missing'});
        }
        const contentType=({'.html':'text/html; charset=utf-8','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)];
        return route.fulfill({status:200,body:fs.readFileSync(file),contentType});
      });
      const page=await context.newPage();page.on('pageerror',e=>failures.push(e.message));
      const settle=async()=>{
        await page.waitForFunction(()=>document.querySelectorAll('main').length===1);
        await page.waitForTimeout(80);
      };
      const checkHead=async relative=>{
        const expected=fs.readFileSync(path.join(ROOT,relative),'utf8');
        const result=await page.evaluate(({html,selector})=>{
          const next=new DOMParser().parseFromString(html,'text/html');
          const collect=doc=>[...doc.head.querySelectorAll(selector)].map(x=>x.outerHTML).sort();
          return {actual:collect(document),expected:collect(next),title:document.title,expectedTitle:next.title,lang:document.documentElement.lang,expectedLang:next.documentElement.lang};
        },{html:expected,selector:headSelector});
        assert.deepEqual(result.actual,result.expected,`${relative}: stale page metadata`);
        assert.equal(result.title,result.expectedTitle);assert.equal(result.lang,result.expectedLang);
      };
      const linkTo=async relative=>{
        await page.locator(`.site-footer a[href="/pai-web/${relative}"]`).first().evaluate(a=>a.click());
        await page.waitForURL(BASE+relative);await settle();
      };
      // Every entry page can navigate Home without relying on a previous Home visit.
      for(const lang of ['', 'en/'])for(const file of files){
        await page.goto(BASE+lang+file);await checkHead(lang+file);
        await page.locator('.site-header .brand').click();await page.waitForURL(BASE+lang);await settle();
        await checkHead(lang+'index.html');await page.locator('#main-content .pai-logo-motion').waitFor();
      }
      console.log(`${width}px: 26 direct entries, return Home, logo and metadata passed`);
      // History restores saved positions; language links retain the matching page.
      await page.goto(BASE+'about.html');await page.evaluate(()=>window.scrollTo(0,600));await page.waitForTimeout(180);
      await linkTo('research.html');await page.evaluate(()=>window.scrollTo(0,350));await page.waitForTimeout(180);
      await page.goBack();await page.waitForURL(BASE+'about.html');await settle();
      assert.ok(Math.abs(await page.evaluate(()=>scrollY)-600)<=2,'Back lost scroll position');await checkHead('about.html');
      await page.goForward();await page.waitForURL(BASE+'research.html');await settle();
      assert.ok(Math.abs(await page.evaluate(()=>scrollY)-350)<=2,'Forward lost scroll position');await checkHead('research.html');
      await linkTo('en/research.html');await checkHead('en/research.html');
      await linkTo('research.html');await checkHead('research.html');
      await linkTo('publications.html');await page.locator('.publication-years').waitFor();
      const toolbar=()=>page.locator('.publication-toolbar').evaluate(e=>({top:getComputedStyle(e).paddingTop,bottom:getComputedStyle(e).paddingBottom}));
      const spacing=await toolbar();await page.reload();await page.locator('.publication-years').waitFor();
      assert.deepEqual(await toolbar(),spacing);await checkHead('publications.html');
      console.log(`${width}px: Back/Forward positions, language switch and reload passed`);
      // A failed request is recoverable without reloading the document.
      failPapers=true;await page.goto(BASE+'publications.html');await page.locator('[data-pub-retry]').waitFor();
      failPapers=false;await page.locator('[data-pub-retry]').click();await page.locator('.pub').first().waitFor();
      const expectedPapers=['data/publications.json','data/publications-archive.json'].reduce((n,f)=>n+JSON.parse(fs.readFileSync(path.join(ROOT,f),'utf8')).length,0);
      assert.equal(await page.locator('.pub').count(),expectedPapers);
      console.log(`${width}px: network failure/retry recovered all ${expectedPapers} papers`);
      if(width===390){
        const cdp=await context.newCDPSession(page);
        const swipe=async(from,to)=>{
          await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:from,y:320}]});
          await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:(from+to)/2,y:320}]});await page.waitForTimeout(80);
          await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:to,y:320}]});
          await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
        };
        for(const lang of ['', 'en/']){
          slowImages=true;await page.goto(BASE+lang+'about.html');await page.waitForTimeout(350);
          await swipe(75,300);await page.waitForURL(BASE+lang);await settle();await checkHead(lang+'index.html');
          await page.locator('#main-content .pai-logo-motion').waitFor();
          await page.waitForFunction(()=>[...document.querySelectorAll('#main-content .home-achievement-story img')].every(i=>i.complete&&i.naturalWidth>0));
          assert.equal(await page.locator('#main-content .home-achievement-story img[loading=eager][decoding=sync]').count(),3);
          await page.waitForTimeout(350);await swipe(300,75);await page.waitForURL(BASE+lang+'about.html');await settle();await checkHead(lang+'about.html');
          slowImages=false;
        }
        const top=page.locator('.menu-btn'),orbit=page.locator('.pai-orbit-toggle');
        await orbit.click();await page.waitForTimeout(650);await top.click();
        assert.equal(await page.locator('.pai-orbit.open').count(),0);assert.equal(await orbit.getAttribute('aria-expanded'),'false');
        assert.equal(await page.locator('.pai-orbit.auto-rotating').count(),0);
        await orbit.click();assert.equal(await top.getAttribute('aria-expanded'),'false');await orbit.click();
        await cdp.detach();console.log('Mobile: bilingual swipes, delayed images and menu exclusivity passed');
        for(const lang of ['', 'en/']){
          await page.goto(BASE+lang);const cta=page.locator('.home-achievements-more a');
          await cta.scrollIntoViewIfNeeded();await page.waitForTimeout(180);
          const originY=await page.evaluate(()=>scrollY);
          await cta.click();await page.waitForURL(BASE+lang+'publications.html');await page.locator('.publication-years').waitFor();
          assert.ok(await page.evaluate(()=>scrollY)<2,'Homepage CTA did not enter at the top');
          await page.goBack();await page.waitForURL(BASE+lang);
          await page.waitForFunction(y=>Math.abs(scrollY-y)<=2,originY);
        }
        await page.goto(BASE);await page.locator('.pai-logo-motion-ready').waitFor({state:'attached'});
        await page.waitForFunction(()=>document.querySelector('.pai-logo-motion-hidden'),{},{timeout:8000});
        await page.reload();await page.locator('.pai-logo-motion-ready').waitFor({state:'attached'});
        assert.equal(await page.locator('.pai-logo-motion-hidden').count(),0,'Reload reused the completed logo state');
        console.log('Mobile: homepage CTA Back positions and logo draw/fade/reload passed');
      }
      // Different translation lengths must preserve the same reading landmark,
      // including papers that only exist in an expanded year group.
      const readingCases=[
        ['index.html','.home-achievement-story',1],
        ['about.html','.platform-conference',0],
        ['research.html','#iotng',0],
        ['team.html','.person',3],
        ['contact.html','.contact-card',0],
        ['join.html','.join-item',1],
        ['people/erwu-liu.html','.detail-block',1],
        ['publications.html','.pub-group[data-year="2025"] .pub',4]
      ];
      for(const [file,selector,index] of readingCases){
        await page.goto(BASE+file);
        if(file==='publications.html'){
          await page.locator('[data-pub-toggle-all]').click();
        }
        const target=page.locator(selector).nth(index);
        await target.waitFor({state:'visible'});
        await page.waitForFunction(()=>[...document.images].every(img=>img.complete));
        await target.evaluate(node=>{
          const r=node.getBoundingClientRect();
          const line=document.querySelector('.site-header').getBoundingClientRect().bottom+16;
          window.scrollTo(0,scrollY+r.top+r.height*.35-line);
        });
        await page.waitForTimeout(180);
        const offset=()=>page.locator(selector).nth(index).evaluate(node=>{
          const r=node.getBoundingClientRect();
          return (document.querySelector('.site-header').getBoundingClientRect().bottom+16-r.top)/r.height;
        });
        const start=await offset();
        const sourceAtBottom=await page.evaluate(()=>document.documentElement.scrollHeight-innerHeight-scrollY<8);
        for(const lang of ['en/','']){
          const destination=lang+(file==='index.html'?'':file);
          await linkTo(destination);
          await page.locator(selector).nth(index).waitFor({state:'visible'});
          if(sourceAtBottom){
            assert.ok(await page.evaluate(()=>document.documentElement.scrollHeight-innerHeight-scrollY<8),`${file}: lost bottom position`);
          }else{
            assert.ok(Math.abs(await offset()-start)<.03,`${width}px ${file}: translation lost content position (${start} -> ${await offset()})`);
          }
        }
      }
      for(const bottom of [false,true]){
        await page.goto(BASE+'about.html');
        if(bottom)await page.evaluate(()=>window.scrollTo(0,document.documentElement.scrollHeight));
        await linkTo('en/about.html');
        assert.ok(await page.evaluate(bottom=>bottom?document.documentElement.scrollHeight-innerHeight-scrollY<2:scrollY<2,bottom));
      }
      console.log(`${width}px: bilingual reading landmarks, expanded papers and page edges passed`);
      await page.evaluate(()=>{sessionStorage.removeItem('pai-page-scroll-v1');localStorage.setItem('pai-lang','zh');});
      await context.close();
    }
    assert.deepEqual(failures,[]);console.log('Navigation acceptance passed; no page errors or missing local resources.');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
