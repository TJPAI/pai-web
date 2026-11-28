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
      const [maxSummary,hideMeta,mobile]=args,fail=[],legacy=[];const eps=0.15;
      const confidentialIds=new Set(['tech-earth','tech-blasting']);
      const newIds=new Set(['tech-uwb-nearlink','tech-short-range-ranging','tech-nearlink-protocol','tech-nearlink-integrated','tech-drone-vision-language','tech-drone-navigation','tech-drone-industrial-inspection']);
      if(cards.filter(c=>newIds.has(c.id)).length!==7)fail.push('expected all seven new achievements');
      function lines(element){
       const r=element.getBoundingClientRect(),h=parseFloat(getComputedStyle(element).lineHeight);
       return h? r.height/h : -1;
      }
      if(mobile && cards.length>=2){const a=cards[0].getBoundingClientRect(),b=cards[1].getBoundingClientRect();if(Math.abs(a.top-b.top)>2||b.left<=a.left||b.left<a.right-1)fail.push('mobile grid must have two columns');}
      // Group cards by their rendered top coordinate, not by a hard-coded column count.
      const rows=[];
      for(const card of cards){
       const top=card.getBoundingClientRect().top;
       let row=rows.find(r=>Math.abs(r.top-top)<=2);
       if(!row){row={top,cards:[]};rows.push(row)}
       row.cards.push(card);
      }
      const fields=[["image",".industry-visual"],["title",".title-item"],["summary",".industry-summary"],...(!hideMeta?[["application",".industry-meta:nth-of-type(2)"],["cooperation",".industry-meta:nth-of-type(3)"]]:[]),["enquiry",".industry-link"]];
      for(const row of rows){
       for(const [name,selector] of fields){
        const applicable=row.cards.filter(c=>!confidentialIds.has(c.id)||name==='image'||name==='title');
        if(!applicable.length)continue;
        const elements=applicable.map(c=>c.querySelector(selector));
        if(elements.some(e=>!e)){fail.push("row missing "+name);continue}
        const tops=elements.map(e=>e.getBoundingClientRect().top);
        if(Math.max(...tops)-Math.min(...tops)>2)fail.push("row "+row.cards.map(c=>c.id).join(",")+" "+name+" vertical offset "+(Math.max(...tops)-Math.min(...tops)).toFixed(2)+"px");
       }
      }
      for(const card of cards){
       const id=card.id, title=card.querySelector(".title-item"),summary=card.querySelector(".industry-summary"),meta=[...card.querySelectorAll(".industry-meta")];
       if(confidentialIds.has(id)){
        const notice=card.querySelector('.industry-confidential');
        if(!title||summary||meta.length||!notice||!card.querySelector('.industry-link')){fail.push(id+': invalid confidential card');continue}
        if(!notice.textContent.includes(document.documentElement.lang.startsWith('zh')?'签署保密协议':'non-disclosure agreement (NDA)'))fail.push(id+': NDA notice missing');
        if(notice.scrollWidth>notice.clientWidth+1||notice.scrollHeight>notice.clientHeight+1||notice.getClientRects().length===0)fail.push(id+': NDA notice clipped');
        continue;
       }
       if(!title||!summary||meta.length!==2){fail.push(id+": missing title, summary or metadata");continue}
       const zh=document.documentElement.lang.toLowerCase().startsWith("zh");
       const countText=el=>Array.from(el.textContent.trim().replace(/\s+/g," ")).length;
       const countMeta=el=>{const copy=el.cloneNode(true);copy.querySelector("b")?.remove();return countText(copy)};
       const counts=[["title",countText(title),zh?9:22,zh?16:36],["summary",countText(summary),zh?22:95,zh?27:105]];
       if(zh)meta.forEach((m,i)=>counts.push([i===0?"application":"cooperation",countMeta(m),9,12]));
       for(const [field,len,min,max] of counts)if(len<min||len>max)fail.push(id+": "+field+" "+len+" characters (range "+min+"–"+max+")");
       const n=lines(title),d=lines(summary),lineIssues=legacy;
       if(n>2+eps)lineIssues.push(id+": title "+n.toFixed(2)+" lines");
       if(d>maxSummary+eps)lineIssues.push(id+": summary "+d.toFixed(2)+" lines");
       for(const m of meta){if(hideMeta){if(getComputedStyle(m).display!=="none"||m.getClientRects().length!==0)fail.push(id+": mobile English metadata visible");continue}if(getComputedStyle(m).display==="none"||m.getClientRects().length===0)fail.push(id+": metadata unexpectedly hidden");const ml=lines(m);if(ml>1+eps)lineIssues.push(id+": metadata "+ml.toFixed(2)+" lines");if(m.scrollWidth>m.clientWidth+1)fail.push(id+": metadata horizontal overflow "+m.scrollWidth+"/"+m.clientWidth)}
       for(const el of [title,summary,...(hideMeta?[]:meta)]){
        if(/…|\.{3}/.test(el.textContent)||getComputedStyle(el).textOverflow==="ellipsis")fail.push(id+": ellipsis");
        const style=getComputedStyle(el);
        if(["hidden","clip"].includes(style.overflowX)||["hidden","clip"].includes(style.overflowY)||(/^\d+$/.test(style.webkitLineClamp)&&Number(style.webkitLineClamp)>0))fail.push(id+": clipped overflow");
        if(el.scrollWidth>el.clientWidth+1||el.scrollHeight>el.clientHeight+1)fail.push(id+": content overflow");
       }
      }
      return {count:cards.length,fail,legacy};
     },[lang==="en" && width>768 ? 2 : limit,lang==="en" && width<=768,width<=768]);
     if(out.count!==21)violations.push(browserName+"/"+lang+"/"+width+": expected 21 cards, got "+out.count);
     violations.push(...out.fail.map(x=>browserName+"/"+lang+"/"+width+": "+x));
     console.log(browserName,lang,width,"cards",out.count,"blocking issues",out.fail.length,"line-limit observations",out.legacy.length);
     for(const issue of out.legacy)console.log("LINE LIMIT (approved character range):",browserName,lang,width,issue);
     await page.close();
    }
   }
  }finally{await browser.close()}
 }
 if(violations.length){console.error("Card line-limit violations:\n"+violations.join("\n"));process.exitCode=1}
 else console.log("PASS: all 21 bilingual cards meet character limits, full visibility and mobile grid; line-count observations reported separately under approved character ranges");
})().catch(e=>{console.error(e);process.exit(1)});
