from pathlib import Path
import re

css_path=Path('assets/css/site.css')
css=css_path.read_text()
old='''\n/* TEMP v36: hide footer for swipe visual test */\n.site-footer{display:none!important}'''
if old not in css:
    raise SystemExit('temporary footer hide rule not found')
css=css.replace(old,'''\n\n/* During an active horizontal page gesture, hide footer paint but preserve its layout height. */\n.site-footer.swipe-footer-hidden{visibility:hidden!important;pointer-events:none!important}''',1)
css_path.write_text(css)

js_path=Path('assets/js/site.js')
js=js_path.read_text()

old='''  let pageSwipeStart=null;\n  let swipePreview=null;\n'''
new='''  let pageSwipeStart=null;\n  let swipePreview=null;\n\n  const setSwipeFooterHidden=hidden=>{\n    const footer=document.querySelector('.site-footer');\n    if(footer) footer.classList.toggle('swipe-footer-hidden',!!hidden);\n  };\n'''
if old not in js:
    raise SystemExit('swipe state block not found')
js=js.replace(old,new,1)

old='''  const destroySwipePreview=()=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    const main=document.querySelector('main');\n    if(main){\n      main.style.transform='';\n      main.style.willChange='';\n    }\n  };\n'''
new='''  const destroySwipePreview=(restoreFooter=true)=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    const main=document.querySelector('main');\n    if(main){\n      main.style.transform='';\n      main.style.willChange='';\n    }\n    if(restoreFooter) setSwipeFooterHidden(false);\n  };\n'''
if old not in js:
    raise SystemExit('destroySwipePreview block not found')
js=js.replace(old,new,1)

old='''    const currentMain=document.querySelector('main');\n    const footer=document.querySelector('.site-footer');\n    /* Anchor the preview to the real main's document-space origin. This stays exact\n       whether the mobile header is fixed or desktop header is sticky. */\n    const mainDocumentTop=Math.max(0,(currentMain?.getBoundingClientRect().top||0)+window.scrollY);\n    const footerRect=footer?.getBoundingClientRect();\n    const footerVisible=!!(footerRect&&footerRect.top>mainDocumentTop&&footerRect.top<innerHeight&&footerRect.bottom>0);\n    const previewBottom=footerVisible?Math.max(mainDocumentTop,Math.min(innerHeight,footerRect.top)):innerHeight;\n    /* When the shared footer is visible, keep it stationary and clip the incoming\n       page to the portion of the viewport currently occupied by main content. */\n    shell.style.bottom=`${Math.max(0,innerHeight-previewBottom)}px`;\n'''
new='''    const currentMain=document.querySelector('main');\n    /* Anchor the preview to the real main's document-space origin. This stays exact\n       whether the mobile header is fixed or desktop header is sticky. */\n    const mainDocumentTop=Math.max(0,(currentMain?.getBoundingClientRect().top||0)+window.scrollY);\n'''
if old not in js:
    raise SystemExit('footer clipping block not found')
js=js.replace(old,new,1)

old='''    if(swipePreview) destroySwipePreview();\n    start.direction=direction;\n'''
new='''    if(swipePreview) destroySwipePreview(false);\n    start.direction=direction;\n'''
if old not in js:
    raise SystemExit('direction preview cleanup block not found')
js=js.replace(old,new,1)

old='''      if(ax>=8&&ax>ay*1.18) start.locked=true;\n'''
new='''      if(ax>=8&&ax>ay*1.18){\n        start.locked=true;\n        /* Hide footer only after the gesture is confirmed horizontal.\n           visibility preserves document height, so saved scroll geometry does not move. */\n        setSwipeFooterHidden(true);\n      }\n'''
if old not in js:
    raise SystemExit('swipe lock line not found')
js=js.replace(old,new,1)

js_path.write_text(js)

# Bust only the assets changed by this iteration across every page.
for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'(assets/css/site\.css)(?:\?v=[^\"\']+)?', r'\1?v=20260920-44', text)
    text=re.sub(r'(assets/js/site\.js)(?:\?v=[^\"\']+)?', r'\1?v=20260920-44', text)
    path.write_text(text)
