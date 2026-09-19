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
    const main=document.querySelector('main');
    if(main){
      main.style.transform='';
      main.style.willChange='';
    }
  };
""",
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
'destroy current main/footer')

rep(
"""    const previewMain=document.importNode(nextMain,true);
    previewMain.removeAttribute('id');
    previewMain.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));
""",
"""    const previewPage=document.createElement('div');
    const previewMain=document.importNode(nextMain,true);
    previewMain.removeAttribute('id');
    previewMain.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));
""",
'create preview page wrapper')

rep(
"""    Object.assign(previewMain.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',
      margin:'0',willChange:'transform',pointerEvents:'none',
      background:getComputedStyle(document.body).backgroundColor||'#fff',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
    shell.appendChild(previewMain);
    document.body.appendChild(shell);
    /* Use the same remembered page position as direct/menu navigation.
       A rendered snapshot is cached when leaving a page, so revisits can preview
       the real vertical position without clamping the final destination value. */
    const previewMaxScroll=Math.max(0,mainDocumentTop+previewMain.scrollHeight-innerHeight);
    const previewScroll=Math.min(targetScroll,previewMaxScroll);
    previewMain.style.top=`${mainDocumentTop-previewScroll}px`;
    swipePreview={shell,main:previewMain,url,direction,targetScroll,previewScroll};
""",
"""    previewMain.style.margin='0';
    previewMain.style.pointerEvents='none';
    previewMain.style.background=getComputedStyle(document.body).backgroundColor||'#fff';
    previewPage.appendChild(previewMain);
    const liveFooter=document.querySelector('.site-footer');
    if(liveFooter){
      const previewFooter=liveFooter.cloneNode(true);
      previewFooter.querySelectorAll('[id]').forEach(node=>node.removeAttribute('id'));
      previewPage.appendChild(previewFooter);
    }
    Object.assign(previewPage.style,{
      position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',
      margin:'0',willChange:'transform',pointerEvents:'none',
      transform:`translate3d(${direction>0?'100%':'-100%'},0,0)`
    });
    shell.appendChild(previewPage);
    document.body.appendChild(shell);
    /* Preview the complete page body (main + footer), using the same remembered
       document scroll position as the final navigation. This keeps the dark footer
       present during the drag and prevents a footer flash at handoff. */
    const previewMaxScroll=Math.max(0,mainDocumentTop+previewPage.scrollHeight-innerHeight);
    const previewScroll=Math.min(targetScroll,previewMaxScroll);
    previewPage.style.top=`${mainDocumentTop-previewScroll}px`;
    swipePreview={shell,page:previewPage,main:previewMain,url,direction,targetScroll,previewScroll};
""",
'preview includes footer')

rep(
"""    const current=document.querySelector('main');
    if(current){
      current.style.willChange='transform';
      current.style.transform=`translate3d(${bounded}px,0,0)`;
    }
    const incoming=bounded+(direction>0?width:-width);
    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;
""",
"""    [document.querySelector('main'),document.querySelector('.site-footer')].forEach(current=>{
      if(!current) return;
      current.style.willChange='transform';
      current.style.transform=`translate3d(${bounded}px,0,0)`;
    });
    const incoming=bounded+(direction>0?width:-width);
    preview.page.style.transform=`translate3d(${incoming}px,0,0)`;
""",
'position main footer together')

rep(
"""  const settleSwipeBack=async()=>{
    const current=document.querySelector('main');
    const preview=swipePreview;
    if(!current||!preview){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=current.style.transform||'translate3d(0,0,0)';
    const incomingFrom=preview.main.style.transform||`translate3d(${preview.direction>0?width:-width}px,0,0)`;
    await Promise.all([
      animateElementTransform(current,currentFrom,'translate3d(0,0,0)',253),
      animateElementTransform(preview.main,incomingFrom,`translate3d(${preview.direction>0?width:-width}px,0,0)`,253)
    ]);
    destroySwipePreview();
  };
""",
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
'settle main footer together')

rep(
"""  const commitSwipe=async(direction)=>{
    const current=document.querySelector('main');
    const preview=swipePreview;
    const start=pageSwipeStart;
    if(!current||!preview||!start){ destroySwipePreview(); return; }
    const width=Math.max(1,innerWidth);
    const currentFrom=current.style.transform||'translate3d(0,0,0)';
    const incomingFrom=preview.main.style.transform||`translate3d(${direction>0?width:-width}px,0,0)`;
    const targetUrl=preview.url;
    const targetScroll=Math.max(0,Number(preview.targetScroll)||0);
    await Promise.all([
      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),
      animateElementTransform(preview.main,incomingFrom,'translate3d(0,0,0)',330)
    ]);
""",
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
    const targetScroll=Math.max(0,Number(preview.targetScroll)||0);
    await Promise.all([
      animateElementTransform(current,currentFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),
      animateElementTransform(footer,footerFrom,`translate3d(${direction>0?-width:width}px,0,0)`,330),
      animateElementTransform(preview.page,incomingFrom,'translate3d(0,0,0)',330)
    ]);
""",
'commit main footer together')

p.write_text(s)

changed=0
for pattern in ('*.html','en/*.html','people/*.html','en/people/*.html'):
    for f in Path('.').glob(pattern):
        html=f.read_text()
        newer=html.replace('site.js?v=20260919-25','site.js?v=20260919-26')
        if newer!=html:
            f.write_text(newer)
            changed+=1
if changed==0:
    raise SystemExit('no v25 references updated')
print(f'patched swipe footer handoff and {changed} HTML files')
