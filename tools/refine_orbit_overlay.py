from pathlib import Path
import re

# 1) Tune character spacing while preserving the accepted 8-sector geometry.
p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old="""        const charStep=ascii
          ? (chars.length<=4?5.4:Math.min(4.2,36/Math.max(1,chars.length-1)))
          : (chars.length<=2?8.2:8.8);"""
new="""        const charStep=ascii
          ? (chars.length<=4?5.0:Math.min(3.6,32/Math.max(1,chars.length-1)))
          : (chars.length<=2?7.8:7.6);"""
if old not in s:
    raise SystemExit('current charStep block not found')
s=s.replace(old,new,1)

# Keep the orbit open when a menu item navigates. Drag suppression remains unchanged.
old_click="""      if(moved){
        e.preventDefault();
        e.stopPropagation();
        moved=false;
        return;
      }
      setOpen(false);
    },true);"""
new_click="""      if(moved){
        e.preventDefault();
        e.stopPropagation();
        moved=false;
        return;
      }
      /* Navigation uses the site's normal delegated handler. Keep the orbit open. */
    },true);"""
if old_click not in s:
    raise SystemExit('orbit click-close block not found')
s=s.replace(old_click,new_click,1)

# The orbit is intentionally persistent: only the center toggle closes it.
s=s.replace("    backdrop.addEventListener('click',()=>setOpen(false));\n","")
s=s.replace("    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&orbit.classList.contains('open'))setOpen(false);});\n","")
p.write_text(s,encoding='utf-8')

# 2) Make it a non-modal floating control: no blur/dim, page stays interactive.
p=Path('assets/css/app-core.css')
s=p.read_text(encoding='utf-8')
repls={
".pai-orbit-backdrop{position:absolute;inset:0;background:rgba(15,18,24,.08);backdrop-filter:blur(2px);-webkit-backdrop-filter:blur(2px);opacity:0;transition:opacity .22s ease;pointer-events:none}":
".pai-orbit-backdrop{position:absolute;inset:0;background:transparent;opacity:0;pointer-events:none}",
"transition:opacity .16s ease,transform .34s cubic-bezier(.16,.84,.2,1)":
"transition:opacity .30s ease,transform .52s cubic-bezier(.16,.84,.2,1)",
"scale(.20) rotate(var(--orbit-rotation,0deg))":
"scale(.06) rotate(var(--orbit-rotation,0deg))",
"transition:transform .26s cubic-bezier(.2,.8,.2,1)":
"transition:transform .40s cubic-bezier(.2,.8,.2,1)",
".pai-orbit.open{pointer-events:auto}":
".pai-orbit.open{pointer-events:none}",
".pai-orbit.open .pai-orbit-backdrop{opacity:1;pointer-events:auto}":
".pai-orbit.open .pai-orbit-backdrop{opacity:0;pointer-events:none}",
}
for a,b in repls.items():
    if a not in s:
        raise SystemExit('css token not found: '+a[:80])
    s=s.replace(a,b,1)
# Ensure the wheel and center toggle themselves remain interactive while the overlay is open.
# Toggle already has pointer-events:auto; wheel open rule already has pointer-events:auto.
# Slightly reduce English glyph size to preserve visible gaps between long labels.
s += '\n@media(max-width:768px){html[lang="en"] .pai-orbit-char{font-size:10.4px}}\n'
p.write_text(s,encoding='utf-8')

# 3) Cache-bust CSS + JS across all pages.
p=Path('assets/css/refine.css')
s=p.read_text(encoding='utf-8')
s=s.replace('./app-core.css?v=20260920-21','./app-core.css?v=20260920-22')
p.write_text(s,encoding='utf-8')

for html in Path('.').rglob('*.html'):
    s=html.read_text(encoding='utf-8')
    s=re.sub(r'refine\.css\?v=[^\"\']+','refine.css?v=20260920-22',s)
    s=re.sub(r'site\.js\?v=[^\"\']+','site.js?v=20260920-63',s)
    html.write_text(s,encoding='utf-8')
