from pathlib import Path
import re

# v40 trigger: detach mobile header from page flow and close overlay before navigation.
css_path=Path('assets/css/site.css')
css=css_path.read_text()
old="""  /* Keep the sticky mobile chrome on a stable Safari compositing layer.\n     Opaque paint avoids intermittent backdrop-filter disappearance during horizontal swipes. */\n  .site-header{background:#fff;backdrop-filter:none;-webkit-backdrop-filter:none;isolation:isolate;z-index:80;transform:translateZ(0);-webkit-transform:translateZ(0);backface-visibility:hidden;-webkit-backface-visibility:hidden}\n  .container{width:min(calc(100% - 36px),var(--max))}\n  .nav{height:62px}.nav-links{display:none}.menu-btn{display:block}.brand strong{font-size:22px}\n"""
new="""  /* Mobile chrome is a permanent overlay, fully detached from page swaps and scroll restoration. */\n  body{padding-top:62px}\n  .site-header{position:fixed;top:0;left:0;right:0;width:100%;background:#fff;backdrop-filter:none;-webkit-backdrop-filter:none;isolation:isolate;z-index:1000;transform:translateZ(0);-webkit-transform:translateZ(0);backface-visibility:hidden;-webkit-backface-visibility:hidden}\n  .container{width:min(calc(100% - 36px),var(--max))}\n  .nav{height:62px}.nav-links{display:none}.menu-btn{display:block}.brand strong{font-size:22px}\n  .site-header .mobile-menu{position:absolute;top:100%;left:0;right:0;background:#fff;max-height:calc(100svh - 62px);overflow:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;box-shadow:0 12px 28px rgba(23,26,31,.08)}\n"""
if old not in css:
    raise SystemExit('mobile header block not found')
css=css.replace(old,new,1)
css_path.write_text(css)

js_path=Path('assets/js/site.js')
js=js_path.read_text()
old_js="""    event.preventDefault();\n    saveCurrentScroll();\n    cacheCurrentPageSnapshot();\n"""
new_js="""    event.preventDefault();\n    /* Close the mobile overlay before navigation begins. Because the menu is fixed\n       outside page flow, this never shifts the destination main or its scroll geometry. */\n    const mobileMenu=link.closest('.mobile-menu');\n    if(mobileMenu){\n      mobileMenu.classList.remove('open');\n      const button=mobileMenu.closest('.site-header')?.querySelector('.menu-btn');\n      if(button) button.setAttribute('aria-expanded','false');\n    }\n    saveCurrentScroll();\n    cacheCurrentPageSnapshot();\n"""
if old_js not in js:
    raise SystemExit('navigation click block not found')
js=js.replace(old_js,new_js,1)
js_path.write_text(js)

for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'assets/css/site\\.css\\?v=20260919-\\d+', 'assets/css/site.css?v=20260920-40', text)
    text=re.sub(r'assets/js/site\\.js\\?v=20260919-\\d+', 'assets/js/site.js?v=20260920-40', text)
    text=re.sub(r'\\.\\./assets/css/site\\.css\\?v=20260919-\\d+', '../assets/css/site.css?v=20260920-40', text)
    text=re.sub(r'\\.\\./assets/js/site\\.js\\?v=20260919-\\d+', '../assets/js/site.js?v=20260920-40', text)
    text=re.sub(r'\\.\\./\\.\\./assets/css/site\\.css\\?v=20260919-\\d+', '../../assets/css/site.css?v=20260920-40', text)
    text=re.sub(r'\\.\\./\\.\\./assets/js/site\\.js\\?v=20260919-\\d+', '../../assets/js/site.js?v=20260920-40', text)
    path.write_text(text)
