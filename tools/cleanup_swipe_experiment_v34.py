from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()
s=s.replace("  const destroySwipePreview=(resetCurrent=true)=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    if(!resetCurrent) return;\n", "  const destroySwipePreview=()=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n")
s=s.replace("    /* Switching neighbor direction must not snap the current page back to zero. */\n    if(swipePreview) destroySwipePreview(false);\n", "    if(swipePreview) destroySwipePreview();\n")
p.write_text(s)

for p in Path('.').rglob('*.html'):
    t=p.read_text()
    t=t.replace('site.js?v=20260919-33','site.js?v=20260919-34')
    p.write_text(t)
