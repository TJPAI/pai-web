from pathlib import Path
import re

# Add a slow clockwise requestAnimationFrame loop. It pauses for direct manipulation
# and resumes from the user's release angle. Auto rotation runs only while open.
p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')

old="""    let rotation=0;
    let dragging=false;
    let moved=false;
    let startAngle=0;
    let startRotation=0;"""
new="""    let rotation=0;
    let dragging=false;
    let moved=false;
    let startAngle=0;
    let startRotation=0;
    let autoRaf=0;
    let autoLastTs=0;
    let autoTimer=0;
    const AUTO_DEG_PER_SECOND=3;"""
if old not in s:
    raise SystemExit('orbit state block not found')
s=s.replace(old,new,1)

old="""    const paint=()=>wheel.style.setProperty('--orbit-rotation',rotation+'deg');
    const pointAngle=e=>{"""
new="""    const paint=()=>wheel.style.setProperty('--orbit-rotation',rotation+'deg');
    const stopAuto=()=>{
      if(autoTimer){clearTimeout(autoTimer);autoTimer=0;}
      if(autoRaf){cancelAnimationFrame(autoRaf);autoRaf=0;}
      autoLastTs=0;
      orbit.classList.remove('auto-rotating');
    };
    const autoTick=ts=>{
      if(!orbit.classList.contains('open')||dragging){stopAuto();return;}
      if(autoLastTs){
        const dt=Math.min(50,ts-autoLastTs);
        rotation+=AUTO_DEG_PER_SECOND*dt/1000;
        paint();
      }
      autoLastTs=ts;
      autoRaf=requestAnimationFrame(autoTick);
    };
    const startAuto=()=>{
      if(autoRaf||dragging||!orbit.classList.contains('open')) return;
      orbit.classList.add('auto-rotating');
      autoLastTs=0;
      autoRaf=requestAnimationFrame(autoTick);
    };
    const scheduleAuto=(delay=100)=>{
      if(autoTimer) clearTimeout(autoTimer);
      autoTimer=setTimeout(()=>{autoTimer=0;startAuto();},delay);
    };
    const pointAngle=e=>{"""
if old not in s:
    raise SystemExit('paint block not found')
s=s.replace(old,new,1)

old="""    const setOpen=open=>{
      orbit.classList.toggle('open',open);
      toggle.setAttribute('aria-expanded',open?'true':'false');
      if(open) sync();
      toggle.setAttribute('aria-label',open?(normalizedPath().startsWith('/en/')?'Close quick menu':'关闭快捷菜单'):(normalizedPath().startsWith('/en/')?'Open quick menu':'打开快捷菜单'));
    };"""
new="""    const setOpen=open=>{
      if(!open) stopAuto();
      orbit.classList.toggle('open',open);
      toggle.setAttribute('aria-expanded',open?'true':'false');
      if(open){
        sync();
        /* Let the opening scale animation finish before continuous rotation starts. */
        scheduleAuto(560);
      }
      toggle.setAttribute('aria-label',open?(normalizedPath().startsWith('/en/')?'Close quick menu':'关闭快捷菜单'):(normalizedPath().startsWith('/en/')?'Open quick menu':'打开快捷菜单'));
    };"""
if old not in s:
    raise SystemExit('setOpen block not found')
s=s.replace(old,new,1)

old="""    const begin=e=>{
      if(!orbit.classList.contains('open')) return;
      dragging=true;
      moved=false;
      orbit.classList.add('dragging');"""
new="""    const begin=e=>{
      if(!orbit.classList.contains('open')) return;
      stopAuto();
      dragging=true;
      moved=false;
      orbit.classList.add('dragging');"""
if old not in s:
    raise SystemExit('begin block not found')
s=s.replace(old,new,1)

old="    const end=()=>{ dragging=false; orbit.classList.remove('dragging'); };"
new="    const end=()=>{ dragging=false; orbit.classList.remove('dragging'); scheduleAuto(120); };"
if old not in s:
    raise SystemExit('end block not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

# During continuous auto rotation, just like direct dragging, transform updates must
# not be interpolated by the open/close transition.
p=Path('assets/css/app-core.css')
s=p.read_text(encoding='utf-8')
old='.pai-orbit.dragging .pai-orbit-wheel{transition:none!important}'
new='.pai-orbit.dragging .pai-orbit-wheel,.pai-orbit.auto-rotating .pai-orbit-wheel{transition:none!important}'
if old not in s:
    raise SystemExit('dragging transition rule not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

# Cache bust both assets.
p=Path('assets/css/refine.css')
s=p.read_text(encoding='utf-8')
s=re.sub(r'\./app-core\.css\?v=[^\"\']+','./app-core.css?v=20260920-25',s,count=1)
p.write_text(s,encoding='utf-8')
for html in Path('.').rglob('*.html'):
    t=html.read_text(encoding='utf-8')
    t=re.sub(r'refine\.css\?v=[^\"\']+','refine.css?v=20260920-25',t)
    t=re.sub(r'site\.js\?v=[^\"\']+','site.js?v=20260920-68',t)
    html.write_text(t,encoding='utf-8')
