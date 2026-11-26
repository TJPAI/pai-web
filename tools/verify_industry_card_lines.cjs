/* Visual regression: complete bilingual industry card text without ellipsis.
 * Run with: node tools/verify_industry_card_lines.cjs
 * Requires playwright and browser engines installed by GitHub Actions.
 */
const { chromium, webkit } = require("playwright");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
(async()=>{
 const violations=[];
 for(const [browserName, engine] of [["Chromium",chromium],["WebKit",webkit]]){
  const browser=await engine.launch({headless:true});
  try{
   for(const [lang,rel,limit] of [["zh","publications.html",2],["en","en/publications.html",4]]){
    for(const width of [1440,1024,768,390,320]){
     const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
     await page.goto(pathToFileURL(path.resolve(rel)).href,{waitUntil:"domcontentloaded"});
     const out=await page.locator(".page-results .industry-six-rows .industry-card").evaluateAll((cards,args)=>{
      const [maxSummary,hideMeta]=args,fail=[];const eps=0.15;
      function lines(element){
       const r=element.getBoundingClientRect(),h=parseFloat(getComputedStyle(element).lineHeight);
       return h? r.height/h : -1;
      }
      for(const card of cards){
       const id=card.id, title=card.querySelector(".title-item"),summary=card.querySelector(".industry-summary"),meta=[...card.querySelectorAll(".industry-meta")];
       if(!title||!summary||meta.length!==2){fail.push(id+": missing title, summary or metadata");continue}
       const n=lines(title),d=lines(summary);
       if(n>2+eps)fail.push(id+": title "+n.toFixed(2)+" lines");
       if(d>maxSummary+eps)fail.push(id+": summary "+d.toFixed(2)+" lines");
       for(const m of meta){if(hideMeta){if(getComputedStyle(m).display!=="none"||m.getClientRects().length!==0)fail.push(id+": mobile English metadata visible");continue}if(getComputedStyle(m).display==="none"||m.getClientRects().length===0)fail.push(id+": metadata unexpectedly hidden");const ml=lines(m);if(ml>1+eps)fail.push(id+": metadata "+ml.toFixed(2)+" lines");if(m.scrollWidth>m.clientWidth+1)fail.push(id+": metadata horizontal overflow "+m.scrollWidth+"/"+m.clientWidth)}
       for(const el of [title,summary,...(hideMeta?[]:meta)]){
        if(/…|\.{3}/.test(el.textContent)||getComputedStyle(el).textOverflow==="ellipsis")fail.push(id+": ellipsis");
        const style=getComputedStyle(el);
        if(["hidden","clip"].includes(style.overflowX)||["hidden","clip"].includes(style.overflowY)||(/^\d+$/.test(style.webkitLineClamp)&&Number(style.webkitLineClamp)>0))fail.push(id+": clipped overflow");
        if(el.scrollWidth>el.clientWidth+1||el.scrollHeight>el.clientHeight+1)fail.push(id+": content overflow");
       }
      }
      return {count:cards.length,fail};
     },[lang==="en" && width>768 ? 2 : limit,lang==="en" && width<=768]);
     if(out.count!==21)violations.push(browserName+"/"+lang+"/"+width+": expected 21 cards, got "+out.count);
     violations.push(...out.fail.map(x=>browserName+"/"+lang+"/"+width+": "+x));
     console.log(browserName,lang,width,"cards",out.count,"issues",out.fail.length);
     await page.close();
    }
   }
  }finally{await browser.close()}
 }
 if(violations.length){console.error("Card line-limit violations:\n"+violations.join("\n"));process.exitCode=1}
 else console.log("PASS: 21 bilingual cards fit at all tested desktop and mobile widths in Chromium and WebKit");
})().catch(e=>{console.error(e);process.exit(1)});
