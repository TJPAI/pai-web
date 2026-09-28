#!/usr/bin/env python3
"""Apply deployment-only runtime optimizations without rewriting source architecture."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_JS = ROOT / 'assets' / 'js' / 'site.js'
INDEX = ROOT / 'index.html'

text = SITE_JS.read_text(encoding='utf-8')

# Desktop does not render the mobile orbit, so avoid creating its DOM/listeners there.
old_orbit = "  };\n  initOrbitMenu();\n\n})();"
new_orbit = "  };\n  const orbitMedia=matchMedia('(max-width:768px)');\n  const ensureOrbitMenu=()=>{if(orbitMedia.matches)initOrbitMenu();};\n  ensureOrbitMenu();\n  if(orbitMedia.addEventListener) orbitMedia.addEventListener('change',ensureOrbitMenu);\n  else orbitMedia.addListener?.(ensureOrbitMenu);\n\n})();"
if text.count(old_orbit) != 1:
    raise SystemExit('site.js orbit bootstrap contract changed; expected exactly one initOrbitMenu() tail')
text = text.replace(old_orbit, new_orbit)

# Retire only the legacy PAI Service Worker scope. Never unregister unrelated Service
# Workers that may share the production origin under a different path.
old_sw_cleanup = "  let siteReady=Promise.resolve();\n  if('serviceWorker' in navigator){\n    siteReady=navigator.serviceWorker.getRegistrations().then(rs=>Promise.all(rs.map(r=>r.unregister()))).catch(()=>{});\n  }"
new_sw_cleanup = "  let siteReady=Promise.resolve();\n  if('serviceWorker' in navigator){\n    const legacyScope=new URL(root('/'),location.origin).href;\n    siteReady=navigator.serviceWorker.getRegistrations().then(rs=>Promise.all(rs.filter(r=>r.scope===legacyScope).map(r=>r.unregister()))).catch(()=>{});\n  }"
if text.count(old_sw_cleanup) != 1:
    raise SystemExit('site.js legacy Service Worker cleanup contract changed')
text = text.replace(old_sw_cleanup, new_sw_cleanup)

# Swipe neighbors only help touch/mobile navigation. Avoid speculative page requests on
# ordinary desktop, and move initial mobile warming off the critical post-load window.
old_swipe_guard = "  const warmSwipeNeighbors=()=>{\n    if(navigator.connection&&navigator.connection.saveData) return;"
new_swipe_guard = "  const warmSwipeNeighbors=()=>{\n    if(innerWidth>768&&!matchMedia('(pointer:coarse)').matches) return;\n    if(navigator.connection&&navigator.connection.saveData) return;"
if text.count(old_swipe_guard) != 1:
    raise SystemExit('site.js swipe warmup contract changed; expected warmSwipeNeighbors guard')
text = text.replace(old_swipe_guard, new_swipe_guard)

old_initial_swipe = "  setTimeout(warmSwipeNeighbors,260);"
new_initial_swipe = "  if('requestIdleCallback' in window) requestIdleCallback(warmSwipeNeighbors,{timeout:1800});\n  else setTimeout(warmSwipeNeighbors,1200);"
if text.count(old_initial_swipe) != 1:
    raise SystemExit('site.js initial swipe warmup contract changed')
text = text.replace(old_initial_swipe, new_initial_swipe)

old_after_nav = "      setTimeout(()=>warmSwipeNeighbors(),40);"
new_after_nav = "      setTimeout(()=>warmSwipeNeighbors(),600);"
if text.count(old_after_nav) != 1:
    raise SystemExit('site.js post-navigation swipe warmup contract changed')
text = text.replace(old_after_nav, new_after_nav)

# A touchstart is strong navigation intent and may preload images. Desktop mouseover is
# weak intent: fetch only the target HTML at low priority instead of up to six images.
old_mouseover = "  document.addEventListener('mouseover',event=>{\n    const link=event.target.closest&&event.target.closest('a');\n    if(link) warmLinkIntent(link);\n  },{capture:true,passive:true});"
new_mouseover = "  document.addEventListener('mouseover',event=>{\n    const link=event.target.closest&&event.target.closest('a');\n    const url=eligiblePageLink(link);\n    if(url) fetchPage(url,{priority:'low'}).catch(()=>{});\n  },{capture:true,passive:true});"
if text.count(old_mouseover) != 1:
    raise SystemExit('site.js desktop hover warmup contract changed')
text = text.replace(old_mouseover, new_mouseover)

# Publications are static deploy assets. Let the browser/CDN apply ordinary HTTP caching
# instead of forcing a network fetch on every fresh document load.
old_static_fetch = "      const response=await fetch(url.href,{credentials:'same-origin',cache:'no-store',priority});"
new_static_fetch = "      const response=await fetch(url.href,{credentials:'same-origin',priority});"
if text.count(old_static_fetch) != 1:
    raise SystemExit('site.js static resource fetch contract changed')
text = text.replace(old_static_fetch, new_static_fetch)

# Runtime-generated DOI links open a new browsing context. Match the static-link privacy
# contract by suppressing both opener access and referrer transmission.
old_doi_rel = 'target="_blank" rel="noopener">DOI ↗</a>'
new_doi_rel = 'target="_blank" rel="noopener noreferrer">DOI ↗</a>'
if text.count(old_doi_rel) != 1:
    raise SystemExit('site.js DOI link privacy contract changed')
text = text.replace(old_doi_rel, new_doi_rel)

# The closed orbit is visually hidden. Keep its links out of the keyboard/accessibility
# navigation order until the menu is actually opened.
old_orbit_set_open = "    const setOpen=open=>{\n      if(open) setMobileMenu(false);\n      if(!open) stopAuto();\n      orbit.classList.toggle('open',open);\n      toggle.setAttribute('aria-expanded',open?'true':'false');\n      if(open){\n        sync();\n        scheduleAuto(560);\n      }\n      toggle.setAttribute('aria-label',open?(normalizedPath().startsWith('/en/')?'Close quick menu':'关闭快捷菜单'):(normalizedPath().startsWith('/en/')?'Open quick menu':'打开快捷菜单'));\n    };"
new_orbit_set_open = "    const syncOrbitA11y=open=>{\n      wheel.setAttribute('aria-hidden',open?'false':'true');\n      wheel.querySelectorAll('a').forEach(link=>{\n        if(open) link.removeAttribute('tabindex');\n        else link.setAttribute('tabindex','-1');\n      });\n    };\n    const setOpen=open=>{\n      if(open) setMobileMenu(false);\n      if(!open) stopAuto();\n      orbit.classList.toggle('open',open);\n      toggle.setAttribute('aria-expanded',open?'true':'false');\n      if(open){\n        sync();\n        syncOrbitA11y(true);\n        scheduleAuto(560);\n      }else{\n        syncOrbitA11y(false);\n      }\n      toggle.setAttribute('aria-label',open?(normalizedPath().startsWith('/en/')?'Close quick menu':'关闭快捷菜单'):(normalizedPath().startsWith('/en/')?'Open quick menu':'打开快捷菜单'));\n    };"
if text.count(old_orbit_set_open) != 1:
    raise SystemExit('site.js orbit accessibility/open-state contract changed')
text = text.replace(old_orbit_set_open, new_orbit_set_open)

old_orbit_initial = "    sync();\n    paint();\n  };"
new_orbit_initial = "    sync();\n    syncOrbitA11y(false);\n    paint();\n  };"
if text.count(old_orbit_initial) != 1:
    raise SystemExit('site.js orbit initial accessibility contract changed')
text = text.replace(old_orbit_initial, new_orbit_initial)

SITE_JS.write_text(text, encoding='utf-8')

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

print('Prepared deployment runtime: early language redirect, scoped legacy SW cleanup, mobile-only and focus-safe orbit, conservative warming, cacheable static data, private DOI links.')
