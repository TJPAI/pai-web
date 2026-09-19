from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()

old="""  const positionSwipePages=dx=>{\n    const start=pageSwipeStart;\n    const preview=swipePreview;\n    if(!start||!preview) return;\n    const width=Math.max(1,innerWidth);\n    const bounded=Math.max(-width,Math.min(width,dx));\n    const direction=preview.direction;\n    if((direction>0&&bounded>0)||(direction<0&&bounded<0)) return;\n    const current=document.querySelector('main');\n    if(current){\n      current.style.willChange='transform';\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\n    }\n    const incoming=bounded+(direction>0?width:-width);\n    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;\n  };\n"""
new="""  const positionSwipePages=dx=>{\n    const start=pageSwipeStart;\n    if(!start) return;\n    const width=Math.max(1,innerWidth);\n    const bounded=Math.max(-width,Math.min(width,dx));\n    const direction=bounded<0?1:-1;\n    const current=document.querySelector('main');\n    if(current){\n      current.style.willChange='transform';\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\n    }\n    const preview=swipePreview;\n    if(!preview||preview.direction!==direction) return;\n    const incoming=bounded+(direction>0?width:-width);\n    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;\n  };\n"""
if old not in s: raise SystemExit('positionSwipePages block not found')
s=s.replace(old,new,1)

old="""  const settleSwipeBack=async()=>{\n    const current=document.querySelector('main');\n    const preview=swipePreview;\n    if(!current||!preview){ destroySwipePreview(); return; }\n    const width=Math.max(1,innerWidth);\n    const currentFrom=current.style.transform||'translate3d(0,0,0)';\n    const incomingFrom=preview.main.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;\n    await Promise.all([\n      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),\n      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)\n    ]);\n    destroySwipePreview();\n  };\n"""
new="""  const settleSwipeBack=async()=>{\n    const current=document.querySelector('main');\n    const preview=swipePreview;\n    if(!current){ destroySwipePreview(); return; }\n    const currentFrom=current.style.transform||'translate3d(0,0,0)';\n    if(!preview){\n      await animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253);\n      destroySwipePreview();\n      return;\n    }\n    const width=Math.max(1,innerWidth);\n    const incomingFrom=preview.main.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;\n    await Promise.all([\n      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),\n      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)\n    ]);\n    destroySwipePreview();\n  };\n"""
if old not in s: raise SystemExit('settleSwipeBack block not found')
s=s.replace(old,new,1)

old="""    const direction=dx<0?1:-1;\n    if(direction!==start.direction){\n      ensureSwipePreview(direction).then(()=>{\n        if(pageSwipeStart===start) positionSwipePages(start.lastDx);\n      });\n    }else{\n      positionSwipePages(dx);\n    }\n"""
new="""    const direction=dx<0?1:-1;\n    /* The current page always follows the finger immediately. Neighbor HTML may\n       arrive later, but it must not change the gesture model. */\n    positionSwipePages(dx);\n    if(direction!==start.direction){\n      ensureSwipePreview(direction).then(()=>{\n        if(pageSwipeStart===start) positionSwipePages(start.lastDx);\n      });\n    }\n"""
if old not in s: raise SystemExit('touchmove direction block not found')
s=s.replace(old,new,1)

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-25','site.js?v=20260919-28')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0: raise SystemExit('no v25 script refs updated')
print(f'patched deterministic swipe timing; updated {changed} HTML files')
