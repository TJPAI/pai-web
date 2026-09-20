from pathlib import Path
import re

# 1) English letters: one fixed, roomier angular spacing across every English label.
p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old='const charStep=ascii?3.6:7.6;'
new='const charStep=ascii?4.8:7.6;'
if old not in s:
    raise SystemExit('unified charStep token not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# 2) Keep opening deliberate, make closing distinctly slower.
p=Path('assets/css/app-core.css')
s=p.read_text(encoding='utf-8')
old='transition:opacity .30s ease,transform .52s cubic-bezier(.16,.84,.2,1);pointer-events:none;touch-action:none;will-change:transform'
new='transition:opacity .48s ease,transform .78s cubic-bezier(.22,.72,.18,1);pointer-events:none;touch-action:none;will-change:transform'
if old not in s:
    raise SystemExit('base orbit transition token not found')
s=s.replace(old,new,1)
open_rule='.pai-orbit.open .pai-orbit-wheel{opacity:1;transform:translate(-50%,-50%) scale(1) rotate(var(--orbit-rotation,0deg));pointer-events:auto}'
open_new='.pai-orbit.open .pai-orbit-wheel{opacity:1;transform:translate(-50%,-50%) scale(1) rotate(var(--orbit-rotation,0deg));pointer-events:auto;transition-duration:.30s,.52s;transition-timing-function:ease,cubic-bezier(.16,.84,.2,1)}'
if open_rule not in s:
    raise SystemExit('open orbit wheel rule not found')
s=s.replace(open_rule,open_new,1)
# Make X -> plus relaxation slower on close; opening keeps the current faster value.
old_toggle='transition:transform .40s cubic-bezier(.2,.8,.2,1)'
new_toggle='transition:transform .58s cubic-bezier(.2,.8,.2,1)'
if old_toggle not in s:
    raise SystemExit('toggle transition token not found')
s=s.replace(old_toggle,new_toggle,1)
open_toggle='.pai-orbit.open .pai-orbit-toggle span{transform:translate(-50%,-50%) rotate(45deg)}'
open_toggle_new='.pai-orbit.open .pai-orbit-toggle span{transform:translate(-50%,-50%) rotate(45deg);transition-duration:.40s}'
if open_toggle not in s:
    raise SystemExit('open toggle rule not found')
s=s.replace(open_toggle,open_toggle_new,1)
p.write_text(s,encoding='utf-8')

# 3) Cache bust both assets.
p=Path('assets/css/refine.css')
s=p.read_text(encoding='utf-8')
s=re.sub(r'\./app-core\.css\?v=[^\"\']+','./app-core.css?v=20260920-23',s,count=1)
p.write_text(s,encoding='utf-8')
for html in Path('.').rglob('*.html'):
    text=html.read_text(encoding='utf-8')
    text=re.sub(r'refine\.css\?v=[^\"\']+','refine.css?v=20260920-23',text)
    text=re.sub(r'site\.js\?v=[^\"\']+','site.js?v=20260920-66',text)
    html.write_text(text,encoding='utf-8')
