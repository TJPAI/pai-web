#!/usr/bin/env python3
"""Apply deployment-only runtime optimizations without rewriting source architecture."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_JS = ROOT / 'assets' / 'js' / 'site.js'

text = SITE_JS.read_text(encoding='utf-8')
old = "  };\n  initOrbitMenu();\n\n})();"
new = "  };\n  const orbitMedia=matchMedia('(max-width:768px)');\n  const ensureOrbitMenu=()=>{if(orbitMedia.matches)initOrbitMenu();};\n  ensureOrbitMenu();\n  if(orbitMedia.addEventListener) orbitMedia.addEventListener('change',ensureOrbitMenu);\n  else orbitMedia.addListener?.(ensureOrbitMenu);\n\n})();"

if text.count(old) != 1:
    raise SystemExit('site.js orbit bootstrap contract changed; expected exactly one initOrbitMenu() tail')

SITE_JS.write_text(text.replace(old, new), encoding='utf-8')
print('Prepared deployment runtime: orbit menu initializes only for mobile-width viewports.')
