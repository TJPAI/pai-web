from pathlib import Path
import re

p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')

old="""  const SWIPE_EDGE_GUARD=32;\n  const SWIPE_MIN_X=58;\n  const SWIPE_FLICK_MIN_X=28;\n  const SWIPE_FLICK_MAX_MS=420;\n  const SWIPE_FLICK_MIN_VX=.30;\n  const SWIPE_MAX_MS=1200;\n  const SWIPE_SETTLE_MS=330;\n  let pageSwipeStart=null;\n  let swipePreview=null;\n"""
new="""  const SWIPE_EDGE_GUARD=32;\n  const SWIPE_MIN_X=58;\n  const SWIPE_FLICK_MIN_X=28;\n  const SWIPE_FLICK_MAX_MS=420;\n  const SWIPE_FLICK_MIN_VX=.30;\n  const SWIPE_MAX_MS=1200;\n  const SWIPE_SETTLE_MS=330;\n  const SWIPE_TEXT_SELECTION_GUARD_MS=420;\n  let pageSwipeStart=null;\n  let swipePreview=null;\n\n  const hasActiveTextSelection=()=>{\n    try{\n      const selection=window.getSelection?.();\n      return !!selection&&selection.rangeCount>0&&!selection.isCollapsed;\n    }catch(_e){\n      return false;\n    }\n  };\n\n  const isSelectableTextTarget=target=>{\n    const element=target instanceof Element?target:target?.parentElement;\n    if(!element) return false;\n    const text=(element.textContent||'').trim();\n    if(!text) return false;\n    try{\n      const style=getComputedStyle(element);\n      return style.userSelect!=='none'&&style.webkitUserSelect!=='none';\n    }catch(_e){\n      return true;\n    }\n  };\n"""
if old not in s:
    raise SystemExit('swipe constants block not found')
s=s.replace(old,new,1)

old_start="""  document.addEventListener('touchstart',event=>{\n    if(event.touches.length!==1){ pageSwipeStart=null; return; }\n    const touch=event.touches[0];\n    if(touch.clientX<=SWIPE_EDGE_GUARD||touch.clientX>=innerWidth-SWIPE_EDGE_GUARD||swipeBlockedTarget(event.target)){\n      pageSwipeStart=null;\n      return;\n    }\n    const path=normalizedPath();\n    const lang=path.startsWith('/en/')?'en':'zh';\n    if(!swipePageOrder[lang].includes(path)){ pageSwipeStart=null; return; }\n    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang,locked:false,direction:0,lastDx:0};\n  },{passive:true});\n"""
new_start="""  document.addEventListener('touchstart',event=>{\n    if(event.touches.length!==1||hasActiveTextSelection()){ pageSwipeStart=null; return; }\n    const touch=event.touches[0];\n    if(touch.clientX<=SWIPE_EDGE_GUARD||touch.clientX>=innerWidth-SWIPE_EDGE_GUARD||swipeBlockedTarget(event.target)){\n      pageSwipeStart=null;\n      return;\n    }\n    const path=normalizedPath();\n    const lang=path.startsWith('/en/')?'en':'zh';\n    if(!swipePageOrder[lang].includes(path)){ pageSwipeStart=null; return; }\n    pageSwipeStart={x:touch.clientX,y:touch.clientY,time:performance.now(),path,lang,locked:false,direction:0,lastDx:0,textCandidate:isSelectableTextTarget(event.target)};\n  },{passive:true});\n"""
if old_start not in s:
    raise SystemExit('touchstart block not found')
s=s.replace(old_start,new_start,1)

old_move="""  document.addEventListener('touchmove',event=>{\n    const start=pageSwipeStart;\n    if(!start||event.touches.length!==1) return;\n    const touch=event.touches[0];\n    const dx=touch.clientX-start.x;\n    const dy=touch.clientY-start.y;\n    const ax=Math.abs(dx);\n    const ay=Math.abs(dy);\n\n    if(!start.locked){\n      if(ax<8&&ay<8) return;\n      if(ay>ax*1.08){ pageSwipeStart=null; return; }\n      if(ax>=8&&ax>ay*1.18) start.locked=true;\n    }\n"""
new_move="""  document.addEventListener('touchmove',event=>{\n    const start=pageSwipeStart;\n    if(!start||event.touches.length!==1) return;\n    const touch=event.touches[0];\n    const dx=touch.clientX-start.x;\n    const dy=touch.clientY-start.y;\n    const ax=Math.abs(dx);\n    const ay=Math.abs(dy);\n\n    if(!start.locked){\n      const held=performance.now()-start.time;\n      if(hasActiveTextSelection()||(start.textCandidate&&held>=SWIPE_TEXT_SELECTION_GUARD_MS)){\n        pageSwipeStart=null;\n        destroySwipePreview();\n        return;\n      }\n      if(ax<8&&ay<8) return;\n      if(ay>ax*1.08){ pageSwipeStart=null; return; }\n      if(ax>=8&&ax>ay*1.18) start.locked=true;\n    }\n"""
if old_move not in s:
    raise SystemExit('touchmove block not found')
s=s.replace(old_move,new_move,1)

anchor="""  document.addEventListener('touchcancel',()=>{\n"""
insert="""  document.addEventListener('selectionchange',()=>{\n    if(!pageSwipeStart||pageSwipeStart.locked||!hasActiveTextSelection()) return;\n    pageSwipeStart=null;\n    destroySwipePreview();\n  });\n\n  document.addEventListener('contextmenu',()=>{\n    if(!pageSwipeStart||pageSwipeStart.locked) return;\n    pageSwipeStart=null;\n    destroySwipePreview();\n  },{passive:true});\n\n"""
if anchor not in s:
    raise SystemExit('touchcancel anchor not found')
s=s.replace(anchor,insert+anchor,1)

p.write_text(s,encoding='utf-8')

for html in Path('.').rglob('*.html'):
    h=html.read_text(encoding='utf-8')
    h=re.sub(r'site\\.js\\?v=[0-9-]+','site.js?v=20260920-57',h)
    html.write_text(h,encoding='utf-8')
