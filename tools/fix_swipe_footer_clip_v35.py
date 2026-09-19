from pathlib import Path

p=Path('assets/js/site.js')
s=p.read_text()
old="""    const currentMain=document.querySelector('main');
    const header=document.querySelector('.site-header');
    const mainDocumentTop=Math.max(0,header?.getBoundingClientRect().bottom||currentMain?.getBoundingClientRect().top||0);
    const targetPath=normalizedPath(url.pathname);
"""
new="""    const currentMain=document.querySelector('main');
    const header=document.querySelector('.site-header');
    const footer=document.querySelector('.site-footer');
    const mainDocumentTop=Math.max(0,header?.getBoundingClientRect().bottom||currentMain?.getBoundingClientRect().top||0);
    const footerRect=footer?.getBoundingClientRect();
    const footerVisible=!!(footerRect&&footerRect.top>mainDocumentTop&&footerRect.top<innerHeight&&footerRect.bottom>0);
    const previewBottom=footerVisible?Math.max(mainDocumentTop,Math.min(innerHeight,footerRect.top)):innerHeight;
    /* When the shared footer is visible, keep it stationary and clip the incoming
       page to the portion of the viewport currently occupied by main content. */
    shell.style.bottom=`${Math.max(0,innerHeight-previewBottom)}px`;
    const targetPath=normalizedPath(url.pathname);
"""
if old not in s:
    raise SystemExit('target block not found')
s=s.replace(old,new,1)
# Remove the now-known ineffective direction-switch experiment, restoring original cleanup semantics.
s=s.replace("""    /* Direction changes during the same gesture must never snap the current page
       back to zero. Remove only the obsolete neighbor preview here. */
    if(swipePreview) destroySwipePreview(false);
""","""    if(swipePreview) destroySwipePreview();
""",1)
p.write_text(s)

for html in Path('.').rglob('*.html'):
    text=html.read_text()
    if 'site.js?v=20260919-34' in text:
        html.write_text(text.replace('site.js?v=20260919-34','site.js?v=20260919-35'))
