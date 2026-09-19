from pathlib import Path

js=Path('assets/js/site.js')
s=js.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s=s.replace(old,new,1)

# Add hard runtime cleanup helpers near the swipe state.
rep(
"""  let pageSwipeStart=null;\n  let swipePreview=null;\n\n  const swipeBlockedTarget=target=>!!(target?.closest&&target.closest(\n""",
"""  let pageSwipeStart=null;\n  let swipePreview=null;\n\n  const cleanupStaleSwipePreviews=()=>{\n    document.querySelectorAll('[data-pai-swipe-preview]').forEach(node=>node.remove());\n  };\n  const enforceSinglePageFooter=()=>{\n    const surface=document.querySelector('.page-surface');\n    if(!surface) return;\n    document.querySelectorAll('.site-footer').forEach(footer=>{\n      if(!surface.contains(footer)) footer.remove();\n    });\n    const footers=[...surface.querySelectorAll('.site-footer')];\n    footers.slice(1).forEach(footer=>footer.remove());\n  };\n  cleanupStaleSwipePreviews();\n  enforceSinglePageFooter();\n\n  const swipeBlockedTarget=target=>!!(target?.closest&&target.closest(\n""",
'add cleanup helpers')

# Make destroy robust even if the JS reference is stale/lost.
rep(
"""  const destroySwipePreview=(resetCurrent=true)=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n""",
"""  const destroySwipePreview=(resetCurrent=true)=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    cleanupStaleSwipePreviews();\n    swipePreview=null;\n""",
'robust destroy')

# Mark every preview shell so it can always be found and removed.
rep(
"""    const shell=document.createElement('div');\n    shell.setAttribute('aria-hidden','true');\n""",
"""    const shell=document.createElement('div');\n    shell.setAttribute('aria-hidden','true');\n    shell.setAttribute('data-pai-swipe-preview','');\n""",
'mark preview shell')

# New gesture always begins from a clean runtime state.
rep(
"""  document.addEventListener('touchstart',event=>{\n    if(event.touches.length!==1){ pageSwipeStart=null; return; }\n""",
"""  document.addEventListener('touchstart',event=>{\n    if(!pageSwipeStart){\n      cleanupStaleSwipePreviews();\n      enforceSinglePageFooter();\n    }\n    if(event.touches.length!==1){ pageSwipeStart=null; return; }\n""",
'clean at touchstart')

# After a real page swap, assert one real footer and remove any orphan preview shell.
rep(
"""      incomingSurface.style.willChange='';\n      setTimeout(()=>warmSwipeNeighbors(),40);\n    }finally{\n      navigating=false;\n    }\n""",
"""      incomingSurface.style.willChange='';\n      enforceSinglePageFooter();\n      setTimeout(()=>warmSwipeNeighbors(),40);\n    }finally{\n      cleanupStaleSwipePreviews();\n      enforceSinglePageFooter();\n      navigating=false;\n    }\n""",
'clean after applyPage')

js.write_text(s)

# Bust JS cache on every static page.
count=0
for f in Path('.').rglob('*.html'):
    if any(part in {'.git','node_modules'} for part in f.parts):
        continue
    t=f.read_text()
    t=t.replace('site.js?v=20260919-30','site.js?v=20260919-31')
    f.write_text(t)
    count+=1
print(f'updated site.js and {count} html files')
