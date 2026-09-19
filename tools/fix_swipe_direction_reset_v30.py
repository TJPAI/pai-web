from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()
old="""  const destroySwipePreview=()=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    const surface=document.querySelector('.page-surface');\n    if(surface){\n      surface.style.transform='';\n      surface.style.willChange='';\n    }\n  };\n"""
new="""  const destroySwipePreview=(resetCurrent=true)=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    if(!resetCurrent) return;\n    const surface=document.querySelector('.page-surface');\n    if(surface){\n      surface.style.transform='';\n      surface.style.willChange='';\n    }\n  };\n"""
if old not in s: raise SystemExit('destroy block not found')
s=s.replace(old,new,1)
old2="""    if(swipePreview) destroySwipePreview();\n    start.direction=direction;\n"""
new2="""    /* Switching neighbor direction must not snap the current page back to zero. */\n    if(swipePreview) destroySwipePreview(false);\n    start.direction=direction;\n"""
if old2 not in s: raise SystemExit('ensure block not found')
s=s.replace(old2,new2,1)
p.write_text(s)

for f in Path('.').rglob('*.html'):
    text=f.read_text()
    text=text.replace('site.js?v=20260919-29','site.js?v=20260919-30')
    f.write_text(text)
print('fixed swipe direction reset and bumped runtime to v30')
