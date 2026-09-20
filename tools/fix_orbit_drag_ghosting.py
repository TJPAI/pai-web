from pathlib import Path
import re

# Disable wheel transition while the user is actively dragging. This prevents
# transform interpolation from trailing the finger and visually double-rendering glyphs.
p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old_begin="""    const begin=e=>{
      if(!orbit.classList.contains('open')) return;
      dragging=true;
      moved=false;
      startAngle=pointAngle(e);
      startRotation=rotation;
      if(e.pointerId!==undefined) wheel.setPointerCapture?.(e.pointerId);
    };"""
new_begin="""    const begin=e=>{
      if(!orbit.classList.contains('open')) return;
      dragging=true;
      moved=false;
      orbit.classList.add('dragging');
      startAngle=pointAngle(e);
      startRotation=rotation;
      if(e.pointerId!==undefined) wheel.setPointerCapture?.(e.pointerId);
    };"""
if old_begin not in s:
    raise SystemExit('begin block not found')
s=s.replace(old_begin,new_begin,1)
old_end="    const end=()=>{ dragging=false; };"
new_end="    const end=()=>{ dragging=false; orbit.classList.remove('dragging'); };"
if old_end not in s:
    raise SystemExit('end block not found')
s=s.replace(old_end,new_end,1)
p.write_text(s,encoding='utf-8')

p=Path('assets/css/app-core.css')
s=p.read_text(encoding='utf-8')
anchor='.pai-orbit.open .pai-orbit-wheel{opacity:1;transform:translate(-50%,-50%) scale(1) rotate(var(--orbit-rotation,0deg));pointer-events:auto;transition-duration:.30s,.52s;transition-timing-function:ease,cubic-bezier(.16,.84,.2,1)}'
if anchor not in s:
    raise SystemExit('open wheel rule not found')
insert=anchor+'\n.pai-orbit.dragging .pai-orbit-wheel{transition:none!important}'
s=s.replace(anchor,insert,1)
# Keep text on its own composited layer to reduce Safari repaint shimmer during rotation.
old_char='pointer-events:none;user-select:none;-webkit-user-select:none;z-index:3}'
new_char='pointer-events:none;user-select:none;-webkit-user-select:none;z-index:3;backface-visibility:hidden;-webkit-backface-visibility:hidden;will-change:transform}'
if old_char not in s:
    raise SystemExit('char rule tail not found')
s=s.replace(old_char,new_char,1)
p.write_text(s,encoding='utf-8')

# Cache bust.
p=Path('assets/css/refine.css')
s=p.read_text(encoding='utf-8')
s=re.sub(r'\./app-core\.css\?v=[^\"\']+','./app-core.css?v=20260920-24',s,count=1)
p.write_text(s,encoding='utf-8')
for html in Path('.').rglob('*.html'):
    t=html.read_text(encoding='utf-8')
    t=re.sub(r'refine\.css\?v=[^\"\']+','refine.css?v=20260920-24',t)
    t=re.sub(r'site\.js\?v=[^\"\']+','site.js?v=20260920-67',t)
    html.write_text(t,encoding='utf-8')
