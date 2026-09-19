from pathlib import Path
import re

js_path=Path('assets/js/site.js')
s=js_path.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s=s.replace(old,new,1)

# Header remains shared chrome; footer is now owned by each page surface.
footer_block='''\n    const footer=document.querySelector('.site-footer');\n    if(footer){\n      const links=items.map(([label,href])=>`<a href="${root(href)}">${label}</a>`).join('')+\n        `<a href="${root(languageHref)}">${languageLabel}</a>`;\n      const contact=lang==='en'?\n        `4800 Cao'an Highway, Jiading District, Shanghai<br>Tongji University Jiading Campus<br><a href="mailto:23666042@tongji.edu.cn">23666042@tongji.edu.cn</a>`:\n        `上海市嘉定区曹安公路4800号<br>同济大学嘉定校区智信馆<br><a href="mailto:23666042@tongji.edu.cn">23666042@tongji.edu.cn</a>`;\n      footer.classList.add('compact-footer');\n      footer.innerHTML=`<div class="container"><div class="footer-grid"><div><div class="brand"><strong>PAI</strong><span>PAI Research Center · Tongji University</span></div></div><div class="footer-links">${links}</div><div class="footer-contact">${contact}</div></div><div class="footer-meta"><span>© PAI Research Center</span></div></div>`;\n    }\n'''
rep(footer_block,'\n','remove shared footer rendering')

rep(
'''      const currentMain=document.querySelector('main');\n      const nextMain=next.querySelector('main');\n      if(!currentMain||!nextMain) throw new Error('page shell unavailable');\n''',
'''      const currentSurface=document.querySelector('.page-surface');\n      const nextSurface=next.querySelector('.page-surface');\n      const currentMain=currentSurface?.querySelector('main');\n      const nextMain=nextSurface?.querySelector('main');\n      if(!currentSurface||!nextSurface||!currentMain||!nextMain) throw new Error('page shell unavailable');\n''',
'apply page surfaces')

rep(
'''      currentMain.style.willChange='transform, opacity';\n      await animateMain(currentMain,[\n''',
'''      currentSurface.style.willChange='transform, opacity';\n      await animateMain(currentSurface,[\n''',
'animate current surface')

rep(
'''      const incomingMain=document.importNode(nextMain,true);\n      currentMain.replaceWith(incomingMain);\n      document.title=next.title||document.title;\n''',
'''      const incomingSurface=document.importNode(nextSurface,true);\n      const incomingMain=incomingSurface.querySelector('main');\n      currentSurface.replaceWith(incomingSurface);\n      document.title=next.title||document.title;\n''',
'replace full page surface')

rep(
'''        await animateMain(incomingMain,[\n''',
'''        await animateMain(incomingSurface,[\n''',
'animate incoming surface')

rep(
'''      incomingMain.style.willChange='';\n''',
'''      incomingSurface.style.willChange='';\n''',
'clear incoming surface hint')

# Swipe cleanup/preview/position/settle/commit operate on whole page surface.
rep(
'''    const main=document.querySelector('main');\n    if(main){\n      main.style.transform='';\n      main.style.willChange='';\n    }\n''',
'''    const surface=document.querySelector('.page-surface');\n    if(surface){\n      surface.style.transform='';\n      surface.style.willChange='';\n    }\n''',
'destroy surface')

rep(
'''    const nextMain=next.querySelector('main');\n    if(!nextMain) return null;\n''',
'''    const nextSurface=next.querySelector('.page-surface');\n    const nextMain=nextSurface?.querySelector('main');\n    if(!nextSurface||!nextMain) return null;\n''',
'preview next surface')

rep(
'''    const previewMain=document.importNode(nextMain,true);\n    previewMain.removeAttribute('id');\n    previewMain.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));\n    previewMain.querySelectorAll('img[src]').forEach(img=>{\n''',
'''    const previewSurface=document.importNode(nextSurface,true);\n    const previewMain=previewSurface.querySelector('main');\n    previewSurface.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));\n    previewSurface.querySelectorAll('img[src]').forEach(img=>{\n''',
'clone full preview surface')

rep(
'''    previewMain.querySelectorAll('source[srcset],img[srcset]').forEach(node=>{\n''',
'''    previewSurface.querySelectorAll('source[srcset],img[srcset]').forEach(node=>{\n''',
'preview srcset surface')

rep(
'''    Object.assign(previewMain.style,{\n      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',\n      margin:'0',willChange:'transform',pointerEvents:'none',\n      background:getComputedStyle(document.body).backgroundColor||'#fff',\n      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`\n    });\n    shell.appendChild(previewMain);\n    document.body.appendChild(shell);\n''',
'''    Object.assign(previewSurface.style,{\n      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',\n      margin:'0',willChange:'transform',pointerEvents:'none',\n      background:getComputedStyle(document.body).backgroundColor||'#fff',\n      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`\n    });\n    shell.appendChild(previewSurface);\n    document.body.appendChild(shell);\n''',
'position full preview surface')

rep(
'''    const previewMaxScroll=Math.max(0,mainDocumentTop+previewMain.scrollHeight-innerHeight);\n    const previewScroll=Math.min(targetScroll,previewMaxScroll);\n    previewMain.style.top=`${mainDocumentTop-previewScroll}px`;\n    swipePreview={shell,main:previewMain,url,direction,targetScroll,previewScroll};\n''',
'''    const previewMaxScroll=Math.max(0,mainDocumentTop+previewSurface.scrollHeight-innerHeight);\n    const previewScroll=Math.min(targetScroll,previewMaxScroll);\n    previewSurface.style.top=`${mainDocumentTop-previewScroll}px`;\n    swipePreview={shell,surface:previewSurface,main:previewMain,url,direction,targetScroll,previewScroll};\n''',
'preview surface scroll')

# v28 position function currently moves current main even before preview is ready.
rep(
'''    const current=document.querySelector('main');\n    if(current){\n      current.style.willChange='transform';\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\n    }\n    if(!preview) return;\n    const direction=preview.direction;\n    if((direction>0&&bounded>0)||(direction<0&&bounded<0)) return;\n    const incoming=bounded+(direction>0?width:-width);\n    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;\n''',
'''    const current=document.querySelector('.page-surface');\n    if(current){\n      current.style.willChange='transform';\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\n    }\n    if(!preview) return;\n    const direction=preview.direction;\n    if((direction>0&&bounded>0)||(direction<0&&bounded<0)) return;\n    const incoming=bounded+(direction>0?width:-width);\n    preview.surface.style.transform=`translate3d(${incoming}px,0,0)`;\n''',
'position current and incoming surfaces')

rep(
'''    const current=document.querySelector('main');\n    const preview=swipePreview;\n    if(!current){ destroySwipePreview(); return; }\n''',
'''    const current=document.querySelector('.page-surface');\n    const preview=swipePreview;\n    if(!current){ destroySwipePreview(); return; }\n''',
'settle current surface')

rep(
'''    const incomingFrom=preview.main.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;\n    await Promise.all([\n      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),\n      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)\n''',
'''    const incomingFrom=preview.surface.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;\n    await Promise.all([\n      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),\n      animateElementTransform(preview.surface,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)\n''',
'settle incoming surface')

rep(
'''    const current=document.querySelector('main');\n    const preview=swipePreview;\n''',
'''    const current=document.querySelector('.page-surface');\n    const preview=swipePreview;\n''',
'commit current surface')

rep(
'''    const incomingFrom=preview.main.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;\n''',
'''    const incomingFrom=preview.surface.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;\n''',
'commit incoming surface from')

rep(
'''      animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',330)\n''',
'''      animateElementTransform(preview.surface,incomingFrom,'translate3d(0,0,0)',330)\n''',
'commit incoming surface animate')

js_path.write_text(s)

# Make main + footer an explicit per-page unit in every static HTML document.
count=0
for f in Path('.').rglob('*.html'):
    if any(part in {'.git','node_modules'} for part in f.parts):
        continue
    text=f.read_text()
    if 'class="page-surface"' not in text:
        new, n = re.subn(r'(<main\b.*?</main>)(<footer\b.*?</footer>)', r'<div class="page-surface">\1\2</div>', text, count=1, flags=re.S)
        if n!=1:
            raise SystemExit(f'could not wrap main+footer in {f}')
        text=new
    text=text.replace('site.js?v=20260919-28','site.js?v=20260919-29')
    f.write_text(text)
    count+=1

print(f'updated site.js and {count} html pages')
