from pathlib import Path
import re

js_path=Path('assets/js/site.js')
js=js_path.read_text()
old="""    const next=new DOMParser().parseFromString(html,'text/html');
    const nextMain=next.querySelector('main');
    const nextFooter=next.querySelector('.site-footer');
    if(!nextMain) return null;
"""
new="""    const next=new DOMParser().parseFromString(html,'text/html');
    const nextMain=next.querySelector('main');
    if(!nextMain) return null;
"""
if old not in js:
    raise SystemExit('target footer parse block not found')
js=js.replace(old,new,1)

old="""    const previewMain=document.importNode(nextMain,true);
    const previewFooter=nextFooter?document.importNode(nextFooter,true):null;
    previewMain.removeAttribute('id');
"""
new="""    const previewMain=document.importNode(nextMain,true);
    /* Top-level swipes never cross languages. Clone the already-rendered live footer
       instead of the raw destination HTML footer, so preview and applyPage/renderChrome
       have identical footer typography, content and height. Strip transient swipe styles. */
    const liveFooter=document.querySelector('.site-footer');
    const previewFooter=liveFooter?liveFooter.cloneNode(true):null;
    if(previewFooter){
      previewFooter.style.removeProperty('transform');
      previewFooter.style.removeProperty('will-change');
    }
    previewMain.removeAttribute('id');
"""
if old not in js:
    raise SystemExit('preview footer clone block not found')
js=js.replace(old,new,1)

js_path.write_text(js)

for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'(assets/js/site\\.js)(?:\\?v=[^\\"\\']+)?', r'\\1?v=20260920-47', text)
    path.write_text(text)
