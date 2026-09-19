from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()
old="""      renderChrome();
      /* Preserve publication expansion state when a rendered snapshot is reused. */
      const preservedPublicationYears=[...next.querySelectorAll('.pub-group[data-expanded=\"true\"]')]
        .map(section=>section.dataset.year).filter(Boolean);
      /* Dynamic page content must settle before restoring a remembered position.
         Publications can substantially change document height after JSON rendering. */
      await initPublications(preservedPublicationYears);
      setTimeout(()=>warmNavigation(),80);
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
      if(Number.isFinite(preserveScrollY)){
        const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        const restoredY=Math.min(Math.max(0,preserveScrollY),maxY);
        scrollToInstant(restoredY);
        rememberPageScroll(normalizedPath(url.pathname),restoredY);
        try{ history.replaceState(historyStateWithScroll(restoredY),'',location.href); }catch(_e){}
      }else if(url.hash){
        document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView();
        const y=rememberPageScroll(normalizedPath(url.pathname),window.scrollY);
        try{ history.replaceState(historyStateWithScroll(y),'',location.href); }catch(_e){}
      }else{
        scrollToInstant(0);
        rememberPageScroll(normalizedPath(url.pathname),0);
        try{ history.replaceState(historyStateWithScroll(0),'',location.href); }catch(_e){}
      }
"""
new="""      renderChrome();

      /* Put the destination at its intended vertical position before Safari gets a
         paint opportunity. Otherwise the freshly swapped main can flash once at
         the outgoing page's scrollY and only then jump to the remembered position. */
      const hasRequestedScroll=Number.isFinite(preserveScrollY);
      if(hasRequestedScroll){
        const provisionalMaxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        scrollToInstant(Math.min(Math.max(0,preserveScrollY),provisionalMaxY));
      }else if(!url.hash){
        scrollToInstant(0);
      }

      /* Preserve publication expansion state when a rendered snapshot is reused. */
      const preservedPublicationYears=[...next.querySelectorAll('.pub-group[data-expanded=\"true\"]')]
        .map(section=>section.dataset.year).filter(Boolean);
      /* Publications can change document height after JSON rendering, so make one
         final no-animation correction after dynamic content has settled. */
      await initPublications(preservedPublicationYears);
      setTimeout(()=>warmNavigation(),80);
      await new Promise(resolve=>requestAnimationFrame(resolve));
      if(hasRequestedScroll){
        const maxY=Math.max(0,document.documentElement.scrollHeight-innerHeight);
        const restoredY=Math.min(Math.max(0,preserveScrollY),maxY);
        if(Math.abs(window.scrollY-restoredY)>1) scrollToInstant(restoredY);
        rememberPageScroll(normalizedPath(url.pathname),restoredY);
        try{ history.replaceState(historyStateWithScroll(restoredY),'',location.href); }catch(_e){}
      }else if(url.hash){
        document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView();
        const y=rememberPageScroll(normalizedPath(url.pathname),window.scrollY);
        try{ history.replaceState(historyStateWithScroll(y),'',location.href); }catch(_e){}
      }else{
        rememberPageScroll(normalizedPath(url.pathname),0);
        try{ history.replaceState(historyStateWithScroll(0),'',location.href); }catch(_e){}
      }
"""
if old not in s:
    raise SystemExit('applyPage restore block not found')
s=s.replace(old,new,1)
p.write_text(s)

for f in list(Path('.').glob('*.html'))+list(Path('en').glob('*.html'))+list(Path('people').glob('*.html'))+list(Path('en/people').glob('*.html')):
    t=f.read_text()
    t=t.replace('site.js?v=20260919-37','site.js?v=20260919-38')
    f.write_text(t)
