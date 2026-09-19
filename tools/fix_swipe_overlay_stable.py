from pathlib import Path
import re

p=Path('assets/js/site.js')
s=p.read_text()
old="""  const destroySwipePreview=()=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    const main=document.querySelector('main');\n    if(main){\n      main.style.transform='';\n      main.style.willChange='';\n    }\n  };"""
new="""  const destroySwipePreview=(resetCurrent=true)=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    if(!resetCurrent) return;\n    const main=document.querySelector('main');\n    if(main){\n      main.style.transform='';\n      main.style.willChange='';\n    }\n  };"""
if old not in s:
    raise SystemExit('destroySwipePreview block not found')
s=s.replace(old,new,1)
old2="""    if(swipePreview) destroySwipePreview();\n    start.direction=direction;"""
new2="""    /* Direction changes during the same gesture must never snap the current page\n       back to zero. Remove only the obsolete neighbor preview here. */\n    if(swipePreview) destroySwipePreview(false);\n    start.direction=direction;"""
if old2 not in s:
    raise SystemExit('direction switch block not found')
s=s.replace(old2,new2,1)
p.write_text(s)

for f in list(Path('.').glob('*.html'))+list(Path('en').glob('*.html')):
    t=f.read_text()
    t2=re.sub(r'site\.js\?v=20260919-\d+', 'site.js?v=20260919-29', t)
    if t2!=t:
        f.write_text(t2)
