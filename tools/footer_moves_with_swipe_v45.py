from pathlib import Path
import re

js_path=Path('assets/js/site.js')
js=js_path.read_text()

# 1) Current live footer must be cleaned with the live main.
old="""  const destroySwipePreview=()=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    const main=document.querySelector('main');\n    if(main){\n      main.style.transform='';\n      main.style.willChange='';\n    }\n  };\n"""
new="""  const destroySwipePreview=()=>{\n    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();\n    swipePreview=null;\n    const main=document.querySelector('main');\n    if(main){\n      main.style.transform='';\n      main.style.willChange='';\n    }\n    const footer=document.querySelector('.site-footer');\n    if(footer){\n      footer.style.transform='';\n      footer.style.willChange='';\n    }\n  };\n"""
if old not in js: raise SystemExit('destroySwipePreview block not found')
js=js.replace(old,new,1)

# 2) Parse and clone destination footer along with destination main.
old="""    const next=new DOMParser().parseFromString(html,'text/html');\n    const nextMain=next.querySelector('main');\n    if(!nextMain) return null;\n"""
new="""    const next=new DOMParser().parseFromString(html,'text/html');\n    const nextMain=next.querySelector('main');\n    const nextFooter=next.querySelector('.site-footer');\n    if(!nextMain) return null;\n"""
if old not in js: raise SystemExit('next main block not found')
js=js.replace(old,new,1)

old="""    const previewMain=document.importNode(nextMain,true);\n    previewMain.removeAttribute('id');\n"""
new="""    const previewMain=document.importNode(nextMain,true);\n    const previewFooter=nextFooter?document.importNode(nextFooter,true):null;\n    previewMain.removeAttribute('id');\n"""
if old not in js: raise SystemExit('preview main import block not found')
js=js.replace(old,new,1)

# 3) Remove old shared-footer clipping logic completely.
old="""    const currentMain=document.querySelector('main');\n    const footer=document.querySelector('.site-footer');\n    /* Anchor the preview to the real main's document-space origin. This stays exact\n       whether the mobile header is fixed or desktop header is sticky. */\n    const mainDocumentTop=Math.max(0,(currentMain?.getBoundingClientRect().top||0)+window.scrollY);\n    const footerRect=footer?.getBoundingClientRect();\n    const footerVisible=!!(footerRect&&footerRect.top>mainDocumentTop&&footerRect.top<innerHeight&&footerRect.bottom>0);\n    const previewBottom=footerVisible?Math.max(mainDocumentTop,Math.min(innerHeight,footerRect.top)):innerHeight;\n    /* When the shared footer is visible, keep it stationary and clip the incoming\n       page to the portion of the viewport currently occupied by main content. */\n    shell.style.bottom=`${Math.max(0,innerHeight-previewBottom)}px`;\n"""
new="""    const currentMain=document.querySelector('main');\n    /* Anchor the preview to the real main's document-space origin. This stays exact\n       whether the mobile header is fixed or desktop header is sticky. */\n    const mainDocumentTop=Math.max(0,(currentMain?.getBoundingClientRect().top||0)+window.scrollY);\n"""
if old not in js: raise SystemExit('footer clipping block not found')
js=js.replace(old,new,1)

# 4) Build destination footer at the real document-flow position immediately after main.
old="""    shell.appendChild(previewMain);\n    document.body.appendChild(shell);\n    /* Use the same remembered page position as direct/menu navigation.\n       A rendered snapshot is cached when leaving a page, so revisits can preview\n       the real vertical position without clamping the final destination value. */\n    const previewMaxScroll=Math.max(0,mainDocumentTop+previewMain.scrollHeight-innerHeight);\n    const previewScroll=Math.min(targetScroll,previewMaxScroll);\n    previewMain.style.top=`${mainDocumentTop-previewScroll}px`;\n    swipePreview={shell,main:previewMain,url,direction,targetScroll,previewScroll};\n"""
new="""    shell.appendChild(previewMain);\n    if(previewFooter){\n      previewFooter.removeAttribute('id');\n      previewFooter.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));\n      Object.assign(previewFooter.style,{\n        position:'absolute',left:'0',width:'100%',margin:'0',willChange:'transform',pointerEvents:'none',\n        transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`\n      });\n      shell.appendChild(previewFooter);\n    }\n    document.body.appendChild(shell);\n    /* Menu and swipe use the same saved target scroll. Preview geometry merely\n       reproduces that document position; it never becomes an independent source. */\n    const previewDocumentHeight=mainDocumentTop+previewMain.scrollHeight+(previewFooter?.scrollHeight||0);\n    const previewMaxScroll=Math.max(0,previewDocumentHeight-innerHeight);\n    const previewScroll=Math.min(targetScroll,previewMaxScroll);\n    previewMain.style.top=`${mainDocumentTop-previewScroll}px`;\n    if(previewFooter) previewFooter.style.top=`${mainDocumentTop+previewMain.scrollHeight-previewScroll}px`;\n    swipePreview={shell,main:previewMain,footer:previewFooter,url,direction,targetScroll,previewScroll};\n"""
if old not in js: raise SystemExit('preview append/scroll block not found')
js=js.replace(old,new,1)

# 5) Move current visible footer with current main, and destination footer with destination main.
old="""    const current=document.querySelector('main');\n    if(current){\n      current.style.willChange='transform';\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\n    }\n    const preview=swipePreview;\n    if(!preview||preview.direction!==direction) return;\n    const incoming=bounded+(direction>0?width:-width);\n    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;\n"""
new="""    const current=document.querySelector('main');\n    if(current){\n      current.style.willChange='transform';\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\n    }\n    const currentFooter=document.querySelector('.site-footer');\n    const footerRect=currentFooter?.getBoundingClientRect();\n    const footerVisible=!!(footerRect&&footerRect.bottom>0&&footerRect.top<innerHeight);\n    if(currentFooter&&footerVisible){\n      currentFooter.style.willChange='transform';\n      currentFooter.style.transform=`translate3d(${bounded}px,0,0)`;\n    }\n    const preview=swipePreview;\n    if(!preview||preview.direction!==direction) return;\n    const incoming=bounded+(direction>0?width:-width);\n    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;\n    if(preview.footer) preview.footer.style.transform=`translate3d(${incoming}px,0,0)`;\n"""
if old not in js: raise SystemExit('positionSwipePages block not found')
js=js.replace(old,new,1)

# 6) Rebound current footer and destination footer with their respective pages.
old="""    const currentFrom=current.style.transform||'translate3d(0,0,0)';\n    if(!preview){\n      await animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253);\n      destroySwipePreview();\n      return;\n    }\n    const width=Math.max(1,innerWidth);\n    const incomingFrom=preview.main.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;\n    await Promise.all([\n      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),\n      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)\n    ]);\n"""
new="""    const currentFrom=current.style.transform||'translate3d(0,0,0)';\n    const currentFooter=document.querySelector('.site-footer');\n    const footerFrom=currentFooter?.style.transform||'translate3d(0,0,0)';\n    if(!preview){\n      await Promise.all([\n        animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),\n        currentFooter?.style.transform?animateElementTransform(currentFooter,footerFrom,'translate3d(0,0,0)',253):Promise.resolve()\n      ]);\n      destroySwipePreview();\n      return;\n    }\n    const width=Math.max(1,innerWidth);\n    const incomingFrom=preview.main.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;\n    const previewFooterFrom=preview.footer?.style.transform||incomingFrom;\n    await Promise.all([\n      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),\n      currentFooter?.style.transform?animateElementTransform(currentFooter,footerFrom,'translate3d(0,0,0)',253):Promise.resolve(),\n      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253),\n      preview.footer?animateElementTransform(preview.footer,previewFooterFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253):Promise.resolve()\n    ]);\n"""
if old not in js: raise SystemExit('settleSwipeBack block not found')
js=js.replace(old,new,1)

# 7) Commit current footer out and destination footer in with their pages.
old="""    const currentFrom=current.style.transform||'translate3d(0,0,0)';\n    const incomingFrom=preview.main.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;\n    const targetUrl=preview.url;\n"""
new="""    const currentFrom=current.style.transform||'translate3d(0,0,0)';\n    const currentFooter=document.querySelector('.site-footer');\n    const footerFrom=currentFooter?.style.transform||'translate3d(0,0,0)';\n    const incomingFrom=preview.main.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;\n    const previewFooterFrom=preview.footer?.style.transform||incomingFrom;\n    const targetUrl=preview.url;\n"""
if old not in js: raise SystemExit('commit swipe preamble not found')
js=js.replace(old,new,1)

old="""    await Promise.all([\n      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),\n      animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',330)\n    ]);\n"""
new="""    await Promise.all([\n      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),\n      currentFooter?.style.transform?animateElementTransform(currentFooter,footerFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330):Promise.resolve(),\n      animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',330),\n      preview.footer?animateElementTransform(preview.footer,previewFooterFrom,'translate3d(0,0,0)',330):Promise.resolve()\n    ]);\n"""
if old not in js: raise SystemExit('commit animation block not found')
js=js.replace(old,new,1)

js_path.write_text(js)

# 8) Footer normal by default: remove the global temporary hide rule.
css_path=Path('assets/css/site.css')
css=css_path.read_text()
old_css='''\n/* TEMP v36: hide footer for swipe visual test */\n.site-footer{display:none!important}'''
if old_css not in css: raise SystemExit('global footer hide rule not found')
css=css.replace(old_css,'',1)
css_path.write_text(css)

# 9) One fresh cache generation for all pages.
for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'(assets/css/site\.css)(?:\?v=[^\"\']+)?', r'\1?v=20260920-45', text)
    text=re.sub(r'(assets/js/site\.js)(?:\?v=[^\"\']+)?', r'\1?v=20260920-45', text)
    path.write_text(text)
