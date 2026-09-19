from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()
old="""  const cacheCurrentPageSnapshot=()=>{\n    try{ pageCache.set(location.href.split('#')[0],document.documentElement.outerHTML); }catch(_e){}\n  };"""
new="""  const cacheCurrentPageSnapshot=()=>{\n    try{\n      /* Never persist transient swipe/compositing state into the page cache.\n         A snapshot may be taken while the live main is still horizontally translated. */\n      const snapshot=document.documentElement.cloneNode(true);\n      const snapshotMain=snapshot.querySelector('main');\n      if(snapshotMain){\n        snapshotMain.style.removeProperty('transform');\n        snapshotMain.style.removeProperty('will-change');\n        snapshotMain.style.removeProperty('opacity');\n      }\n      pageCache.set(location.href.split('#')[0],snapshot.outerHTML);\n    }catch(_e){}\n  };"""
if old not in s:
    raise SystemExit('cache snapshot block not found')
s=s.replace(old,new,1)
p.write_text(s)

for hp in list(Path('.').glob('*.html'))+list(Path('en').rglob('*.html'))+list(Path('people').rglob('*.html')):
    t=hp.read_text()
    t2=t.replace('assets/js/site.js?v=20260919-34','assets/js/site.js?v=20260919-37').replace('../assets/js/site.js?v=20260919-34','../assets/js/site.js?v=20260919-37').replace('../../assets/js/site.js?v=20260919-34','../../assets/js/site.js?v=20260919-37')
    if t2!=t:
        hp.write_text(t2)
