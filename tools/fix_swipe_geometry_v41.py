from pathlib import Path
import re

js_path=Path('assets/js/site.js')
js=js_path.read_text()
old="""    const currentMain=document.querySelector('main');
    const header=document.querySelector('.site-header');
    const footer=document.querySelector('.site-footer');
    const mainDocumentTop=Math.max(0,header?.getBoundingClientRect().bottom||currentMain?.getBoundingClientRect().top||0);
"""
new="""    const currentMain=document.querySelector('main');
    const footer=document.querySelector('.site-footer');
    /* Anchor the preview to the real main's document-space origin. This stays exact
       whether the mobile header is fixed or desktop header is sticky. */
    const mainDocumentTop=Math.max(0,(currentMain?.getBoundingClientRect().top||0)+window.scrollY);
"""
if old not in js:
    raise SystemExit('mainDocumentTop block not found')
js=js.replace(old,new,1)
js=js.replace("position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',minHeight:'100vh',", "position:'absolute',top:`${mainDocumentTop}px`,left:'0',width:'100%',", 1)
old_commit="""    const targetUrl=preview.url;
    const targetScroll=rememberedPageScroll(normalizedPath(targetUrl.pathname));
"""
new_commit="""    const targetUrl=preview.url;
    /* Handoff at exactly the vertical position the user already sees in the preview.
       Re-reading an unclamped remembered value here can cause a visible correction jump. */
    const targetScroll=Number.isFinite(preview.previewScroll)?preview.previewScroll:rememberedPageScroll(normalizedPath(targetUrl.pathname));
"""
if old_commit not in js:
    raise SystemExit('commit targetScroll block not found')
js=js.replace(old_commit,new_commit,1)
js_path.write_text(js)

# Force one cache generation across every HTML page, regardless of the previous date/version.
for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'(assets/css/site\\.css)(?:\\?v=[^\"\']+)?', r'\\1?v=20260920-41', text)
    text=re.sub(r'(assets/js/site\\.js)(?:\\?v=[^\"\']+)?', r'\\1?v=20260920-41', text)
    path.write_text(text)
