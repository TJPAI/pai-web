#!/usr/bin/env python3
"""Apply deployment-only runtime optimizations without rewriting source architecture."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_JS = ROOT / 'assets' / 'js' / 'site.js'
INDEX = ROOT / 'index.html'

# Desktop does not render the mobile orbit, so avoid creating its DOM/listeners there.
text = SITE_JS.read_text(encoding='utf-8')
old = "  };\n  initOrbitMenu();\n\n})();"
new = "  };\n  const orbitMedia=matchMedia('(max-width:768px)');\n  const ensureOrbitMenu=()=>{if(orbitMedia.matches)initOrbitMenu();};\n  ensureOrbitMenu();\n  if(orbitMedia.addEventListener) orbitMedia.addEventListener('change',ensureOrbitMenu);\n  else orbitMedia.addListener?.(ensureOrbitMenu);\n\n})();"
if text.count(old) != 1:
    raise SystemExit('site.js orbit bootstrap contract changed; expected exactly one initOrbitMenu() tail')
SITE_JS.write_text(text.replace(old, new), encoding='utf-8')

# Resolve the root-page language preference in <head>, before CSS and eager homepage
# imagery start loading. site.js retains the same redirect as a defensive fallback.
index = INDEX.read_text(encoding='utf-8')
marker = '</script><title>'
if index.count(marker) != 1:
    raise SystemExit('index.html head bootstrap contract changed; expected one script/title boundary')
bootstrap = (
    "</script><script>(function(){try{var s=localStorage.getItem('pai-lang'),"
    "p=(navigator.languages&&navigator.languages[0])||navigator.language||'en',"
    "e=s||(String(p).toLowerCase().startsWith('zh')?'zh':'en'),"
    "b=/bot|crawler|spider|slurp/i.test(navigator.userAgent||'');"
    "if(!b&&e==='en'){location.replace(new URL('en/',location.href).href)}}catch(_){}})();"
    "</script><title>"
)
INDEX.write_text(index.replace(marker, bootstrap), encoding='utf-8')

print('Prepared deployment runtime: mobile-only orbit plus early root-page language redirect.')
