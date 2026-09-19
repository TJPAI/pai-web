from pathlib import Path
import re

root = Path('.')
js_path = root / 'assets/js/site.js'
text = js_path.read_text(encoding='utf-8')
old = """  const animateElementTransform=(node,from,to,duration=SWIPE_SETTLE_MS)=>new Promise(resolve=>{\n    if(!node){ resolve(); return; }\n    if(matchMedia('(prefers-reduced-motion: reduce)').matches||typeof node.animate!=='function'){\n      node.style.transform=to;\n      resolve();\n      return;\n    }\n    try{\n      const animation=node.animate([{transform:from},{transform:to}],{\n        duration,easing:'cubic-bezier(.22,.72,.22,1)',fill:'forwards'\n      });\n      animation.finished.catch(()=>{}).finally(resolve);\n    }catch(_e){\n      node.style.transform=to;\n      resolve();\n    }\n  });\n"""
new = """  const animateElementTransform=(node,from,to,duration=SWIPE_SETTLE_MS)=>new Promise(resolve=>{\n    if(!node){ resolve(); return; }\n    if(matchMedia('(prefers-reduced-motion: reduce)').matches||typeof node.animate!=='function'){\n      node.style.transform=to;\n      resolve();\n      return;\n    }\n    try{\n      const animation=node.animate([{transform:from},{transform:to}],{\n        duration,easing:'cubic-bezier(.22,.72,.22,1)',fill:'forwards'\n      });\n      animation.finished.then(()=>{\n        /* Persist the final value in inline style, then remove the WAAPI effect.\n           A finished fill:forwards animation otherwise keeps overriding the next swipe. */\n        node.style.transform=to;\n        animation.cancel();\n      }).catch(()=>{\n        node.style.transform=to;\n        try{ animation.cancel(); }catch(_e){}\n      }).finally(resolve);\n    }catch(_e){\n      node.style.transform=to;\n      resolve();\n    }\n  });\n"""
if old not in text:
    raise SystemExit('target animation block not found')
text = text.replace(old, new, 1)
js_path.write_text(text, encoding='utf-8')

for p in root.rglob('*.html'):
    s = p.read_text(encoding='utf-8')
    ns = re.sub(r'site\.js\?v=20260919-\d+', 'site.js?v=20260919-33', s)
    if ns != s:
        p.write_text(ns, encoding='utf-8')

print('patched WAAPI residue and bumped site.js to v33')
