from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s=s.replace(old,new,1)

rep(
"""  const destroySwipePreview=()=>{
    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();
    swipePreview=null;
    [document.querySelector('main'),document.querySelector('.site-footer')].forEach(node=>{
      if(!node) return;
      node.style.transform='';
      node.style.willChange='';
    });
  };
""",
"""  const destroySwipePreview=()=>{
    if(swipePreview?.shell?.isConnected) swipePreview.shell.remove();
    swipePreview=null;
    [document.querySelector('main'),document.querySelector('.site-footer')].forEach(node=>{
      if(!node) return;
      node.style.visibility='';
      node.style.transform='';
      node.style.willChange='';
    });
  };
""",
'destroy swipe preview')

rep(
"""    const previewPage=document.createElement('div');
    const previewMain=document.importNode(nextMain,true);
""",
"""    const previewPage=document.createElement('div');
    const currentPage=document.createElement('div');
    const previewMain=document.importNode(nextMain,true);
""",
'create current snapshot wrapper')

rep(
"""    const currentMain=document.querySelector('main');
    const header=document.querySelector('.site-header');
    const mainDocumentTop=Math.max(0,header?.getBoundingClientRect().bottom||currentMain?.getBoundingClientRect().top||0);
    const targetPath=normalizedPath(url.pathname);
    const targetScroll=rememberedPageScroll(targetPath);
""",
"""    const currentMain=document.querySelector('main');
    const currentFooter=document.querySelector('.site-footer');
    const header=document.querySelector('.site-header');
    const mainDocumentTop=Math.max(0,header?.getBoundingClientRect().bottom||currentMain?.getBoundingClientRect().top||0);
    const targetPath=normalizedPath(url.pathname);
    const targetScroll=rememberedPageScroll(targetPath);

    if(currentMain){
      const currentMainClone=currentMain.cloneNode(true);
      currentMainClone.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));
      currentPage.appendChild(currentMainClone);
    }
    if(currentFooter){
      const currentFooterClone=currentFooter.cloneNode(true);
      currentFooterClone.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));
      currentPage.appendChild(currentFooterClone);
    }
""",
'clone current page')

rep(
"""    Object.assign(previewPage.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',
      margin:'0',willChange:'transform',pointerEvents:'none',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
    shell.appendChild(previewPage);
    document.body.appendChild(shell);
""",
"""    Object.assign(currentPage.style,{
      position:'absolute',top:`${mainDocumentTop-window.scrollY}px`,left:'0',width:'100%',minHeight:'100vh',
      margin:'0',willChange:'transform',pointerEvents:'none',transform:'translate3d(0,0,0)'
    });
    Object.assign(previewPage.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',
      margin:'0',willChange:'transform',pointerEvents:'none',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
    shell.appendChild(currentPage);
    shell.appendChild(previewPage);
    document.body.appendChild(shell);
    [currentMain,currentFooter].forEach(node=>{ if(node) node.style.visibility='hidden'; });
""",
'append dual snapshots')

rep(
"""    swipePreview={shell,page:previewPage,main:previewMain,url,direction,targetScroll,previewScroll};
""",
"""    swipePreview={shell,currentPage,page:previewPage,main:previewMain,url,direction,targetScroll,previewScroll};
""",
'store current snapshot')

rep(
"""    [document.querySelector('main'),document.querySelector('.site-footer')].forEach(current=>{
      if(!current) return;
      current.style.willChange='transform';
      current.style.transform=`translate3d(${bounded}px,0,0)`;
    });
    const incoming=bounded+(direction>0?width:-width);
    preview.page.style.transform=`translate3d(${incoming}px,0,0)`;
""",
"""    preview.currentPage.style.transform=`translate3d(${bounded}px,0,0)`;
    const incoming=bounded+(direction>0?width:-width);
    preview.page.style.transform=`translate3d(${incoming}px,0,0)`;
""",
'position snapshot pages')

rep(
"""  const settleSwipeBack=async()=>{
    const current=document.querySelector('main');
    const footer=document.querySelector('.site-footer');
    const preview=swipePreview;
    if(!current||!preview){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=current.style.transform||'translate3d(0,0,0)';
    const footerFrom=footer?.style.transform||currentFrom;
    const incomingFrom=preview.page.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;
    await Promise.all([
      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),
      animateElementTransform(footer,footerFrom,'translate3d(0,0,0)',253),
      animateElementTransform(preview.page,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)
    ]);
    destroySwipePreview();
  };
""",
"""  const settleSwipeBack=async()=>{
    const preview=swipePreview;
    if(!preview){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=preview.currentPage.style.transform||'translate3d(0,0,0)';
    const incomingFrom=preview.page.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;
    await Promise.all([
      animateElementTransform(preview.currentPage,currentFrom,'translate3d(0,0,0)',253),
      animateElementTransform(preview.page,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)
    ]);
    destroySwipePreview();
  };
""",
'settle snapshots')

rep(
"""  const commitSwipe=async(direction)=>{
    const current=document.querySelector('main');
    const footer=document.querySelector('.site-footer');
    const preview=swipePreview;
    const start=pageSwipeStart;
    if(!current||!preview||!start){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=current.style.transform||'translate3d(0,0,0)';
    const footerFrom=footer?.style.transform||currentFrom;
    const incomingFrom=preview.page.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;
    const targetUrl=preview.url;
    const targetScroll=rememberedPageScroll(normalizedPath(targetUrl.pathname));
    await Promise.all([
      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),
      animateElementTransform(footer,footerFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),
      animateElementTransform(preview.page,incomingFrom,'translate3d(0,0,0)',330)
    ]);
""",
"""  const commitSwipe=async(direction)=>{
    const preview=swipePreview;
    const start=pageSwipeStart;
    if(!preview||!start){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=preview.currentPage.style.transform||'translate3d(0,0,0)';
    const incomingFrom=preview.page.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;
    const targetUrl=preview.url;
    const targetScroll=rememberedPageScroll(normalizedPath(targetUrl.pathname));
    await Promise.all([
      animateElementTransform(preview.currentPage,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),
      animateElementTransform(preview.page,incomingFrom,'translate3d(0,0,0)',330)
    ]);
""",
'commit snapshots')

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-26','site.js?v=20260919-27')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v26 references updated')
print(f'patched dual snapshot swipe and {changed} HTML files')
