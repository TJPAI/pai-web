from pathlib import Path
import subprocess
import re

BASE='da6a42ad19983412596e17be18c136fda1cdd170'

def from_base(path):
    return subprocess.check_output(['git','show',f'{BASE}:{path}'], text=True)

# Start from the exact pre-orbit stable implementation for the behavior/style files.
js = from_base('assets/js/site.js')
css = from_base('assets/css/app-core.css')
refine = from_base('assets/css/refine.css')

# Orbit gestures must never become page-swipe gestures.
needle = "'a,button,input,textarea,select,option,label,[contenteditable=\"true\"],[role=\"button\"],[data-no-swipe]'"
replacement = "'.pai-orbit,a,button,input,textarea,select,option,label,[contenteditable=\"true\"],[role=\"button\"],[data-no-swipe]'"
if needle not in js:
    raise SystemExit('swipeBlockedTarget selector not found in pre-orbit base')
js = js.replace(needle, replacement, 1)

orbit_js = r'''

  /* PAI orbit menu — rebuilt from the pre-orbit stable site.
     One geometry rule only: item angle = base angle + wheel rotation.
     Therefore every item is upright whenever it reaches 12 o'clock. */
  const initOrbitMenu=()=>{
    if(document.querySelector('.pai-orbit')) return;
    const orbit=document.createElement('div');
    orbit.className='pai-orbit';
    orbit.innerHTML='<div class="pai-orbit-backdrop" aria-hidden="true"></div><div class="pai-orbit-wheel" role="navigation"></div><button class="pai-orbit-toggle" type="button" aria-expanded="false"><span aria-hidden="true"></span></button>';
    document.body.appendChild(orbit);

    const wheel=orbit.querySelector('.pai-orbit-wheel');
    const toggle=orbit.querySelector('.pai-orbit-toggle');
    const backdrop=orbit.querySelector('.pai-orbit-backdrop');
    let rotation=0;
    let dragging=false;
    let moved=false;
    let startAngle=0;
    let startRotation=0;

    const menuData=()=>{
      const en=normalizedPath().startsWith('/en/');
      return en?[
        ['Home','/en/'],['About','/en/about.html'],['People','/en/team.html'],['Research','/en/research.html'],
        ['Publications','/en/publications.html'],['Join','/en/join.html'],['Contact','/en/contact.html'],['中文',counterpartWithContext(normalizedPath())]
      ]:[
        ['首页','/'],['关于','/about.html'],['团队','/team.html'],['研究','/research.html'],
        ['成果','/publications.html'],['加入','/join.html'],['联系','/contact.html'],['EN',counterpartWithContext(normalizedPath())]
      ];
    };

    const sync=()=>{
      const en=normalizedPath().startsWith('/en/');
      const data=menuData();
      wheel.innerHTML=data.map(([label,href],i)=>
        `<a class="pai-orbit-item" href="${root(href)}" style="--item-angle:${i*45}deg"><span>${label}</span></a>`
      ).join('');
      wheel.setAttribute('aria-label',en?'Quick navigation':'快捷导航');
      toggle.setAttribute('aria-label',orbit.classList.contains('open')?(en?'Close quick menu':'关闭快捷菜单'):(en?'Open quick menu':'打开快捷菜单'));
    };

    const paint=()=>wheel.style.setProperty('--orbit-rotation',rotation+'deg');
    const pointAngle=e=>{
      const rect=wheel.getBoundingClientRect();
      const p=e.touches?e.touches[0]:e;
      return Math.atan2(p.clientY-(rect.top+rect.height/2),p.clientX-(rect.left+rect.width/2))*180/Math.PI;
    };
    const setOpen=open=>{
      orbit.classList.toggle('open',open);
      toggle.setAttribute('aria-expanded',open?'true':'false');
      if(open) sync();
      toggle.setAttribute('aria-label',open?(normalizedPath().startsWith('/en/')?'Close quick menu':'关闭快捷菜单'):(normalizedPath().startsWith('/en/')?'Open quick menu':'打开快捷菜单'));
    };
    const begin=e=>{
      if(!orbit.classList.contains('open')) return;
      dragging=true;
      moved=false;
      startAngle=pointAngle(e);
      startRotation=rotation;
      if(e.pointerId!==undefined) wheel.setPointerCapture?.(e.pointerId);
    };
    const move=e=>{
      if(!dragging) return;
      const delta=pointAngle(e)-startAngle;
      if(Math.abs(delta)>3) moved=true;
      rotation=startRotation+delta;
      paint();
    };
    const end=()=>{ dragging=false; };

    toggle.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();setOpen(!orbit.classList.contains('open'));});
    backdrop.addEventListener('click',()=>setOpen(false));

    if(window.PointerEvent){
      wheel.addEventListener('pointerdown',e=>{e.stopPropagation();begin(e);});
      wheel.addEventListener('pointermove',e=>{if(dragging)e.preventDefault();e.stopPropagation();move(e);});
      wheel.addEventListener('pointerup',e=>{e.stopPropagation();end();});
      wheel.addEventListener('pointercancel',end);
    }else{
      wheel.addEventListener('touchstart',e=>{if(e.touches.length===1){e.stopPropagation();begin(e);}},{passive:true});
      wheel.addEventListener('touchmove',e=>{if(dragging&&e.touches.length===1){e.preventDefault();e.stopPropagation();move(e);}},{passive:false});
      wheel.addEventListener('touchend',e=>{e.stopPropagation();end();},{passive:true});
      wheel.addEventListener('touchcancel',end,{passive:true});
    }

    /* Do not create a parallel navigation system. These remain ordinary anchors,
       so the site's existing delegated click handler applies the exact same
       destinationScrollForPath/history behavior as the top navigation. */
    wheel.addEventListener('click',e=>{
      const link=e.target.closest&&e.target.closest('a');
      if(!link) return;
      if(moved){
        e.preventDefault();
        e.stopPropagation();
        moved=false;
        return;
      }
      setOpen(false);
    },true);

    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&orbit.classList.contains('open'))setOpen(false);});
    new MutationObserver(()=>{if(orbit.classList.contains('open'))sync();}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
    sync();
    paint();
  };
  initOrbitMenu();
'''

if not re.search(r'\n\}\)\(\);\s*$', js):
    raise SystemExit('site.js closing wrapper not found')
js = re.sub(r'\n\}\)\(\);\s*$', orbit_js + '\n})();\n', js)

orbit_css = r'''

/* PAI orbit quick menu — clean rebuild from the pre-orbit stable CSS. */
.pai-orbit{position:fixed;inset:0;z-index:1200;pointer-events:none;--orbit-size:min(52vw,220px);--orbit-x:50%;--orbit-y:calc(100dvh - 122px)}
.pai-orbit-backdrop{position:absolute;inset:0;background:rgba(15,18,24,.08);backdrop-filter:blur(2px);-webkit-backdrop-filter:blur(2px);opacity:0;transition:opacity .22s ease;pointer-events:none}
.pai-orbit-wheel{position:absolute;left:var(--orbit-x);top:var(--orbit-y);width:var(--orbit-size);height:var(--orbit-size);border-radius:50%;background:rgba(255,255,255,.98);box-shadow:0 14px 42px rgba(20,24,32,.14);opacity:0;transform:translate(-50%,-50%) scale(.20) rotate(var(--orbit-rotation,0deg));transform-origin:50% 50%;transition:opacity .16s ease,transform .34s cubic-bezier(.16,.84,.2,1);pointer-events:none;touch-action:none;will-change:transform}
.pai-orbit-wheel:before{content:"";position:absolute;inset:32%;border:1px solid rgba(23,26,31,.06);border-radius:50%;pointer-events:none}
.pai-orbit-item{position:absolute;left:50%;top:50%;width:66px;height:30px;margin:-15px 0 0 -33px;display:flex;align-items:center;justify-content:center;color:#171A1F;text-decoration:none;font-size:11.5px;font-weight:620;letter-spacing:.035em;transform:rotate(var(--item-angle)) translateY(calc(var(--orbit-size)*-.395));transform-origin:50% 50%;-webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none}
.pai-orbit-item span{display:block;white-space:nowrap;pointer-events:none}
.pai-orbit-toggle{position:absolute;left:var(--orbit-x);top:var(--orbit-y);width:54px;height:54px;transform:translate(-50%,-50%);border:1px solid rgba(23,26,31,.09);border-radius:50%;background:#fff;box-shadow:0 5px 16px rgba(20,24,32,.09);pointer-events:auto;cursor:pointer;-webkit-tap-highlight-color:transparent}
.pai-orbit-toggle span,.pai-orbit-toggle span:after{position:absolute;content:"";left:50%;top:50%;width:19px;height:1.4px;background:#171A1F;border-radius:2px;transform:translate(-50%,-50%);transition:transform .26s cubic-bezier(.2,.8,.2,1)}
.pai-orbit-toggle span:after{transform:translate(-50%,-50%) rotate(90deg)}
.pai-orbit.open{pointer-events:auto}
.pai-orbit.open .pai-orbit-backdrop{opacity:1;pointer-events:auto}
.pai-orbit.open .pai-orbit-wheel{opacity:1;transform:translate(-50%,-50%) scale(1) rotate(var(--orbit-rotation,0deg));pointer-events:auto}
.pai-orbit.open .pai-orbit-toggle span{transform:translate(-50%,-50%) rotate(45deg)}
.pai-orbit.open .pai-orbit-toggle span:after{transform:translate(-50%,-50%) rotate(90deg)}
@media(min-width:769px){.pai-orbit{--orbit-size:240px;--orbit-y:calc(100dvh - 136px)}.pai-orbit-toggle{width:58px;height:58px}}
@media(max-width:390px){.pai-orbit{--orbit-size:min(54vw,210px);--orbit-y:calc(100dvh - 117px)}}
@media(prefers-reduced-motion:reduce){.pai-orbit *{transition:none!important}}
'''
css = css.rstrip() + orbit_css + '\n'

# Keep the pre-orbit refine content, only point its app-core import to the new cache key.
refine = re.sub(r'app-core\.css\?v=[0-9-]+', 'app-core.css?v=20260920-19', refine)

Path('assets/js/site.js').write_text(js,encoding='utf-8')
Path('assets/css/app-core.css').write_text(css,encoding='utf-8')
Path('assets/css/refine.css').write_text(refine,encoding='utf-8')

# Cache-bust all pages while keeping their current content/metadata intact.
for p in Path('.').rglob('*.html'):
    h=p.read_text(encoding='utf-8')
    h=re.sub(r'refine\.css\?v=[0-9-]+','refine.css?v=20260920-19',h)
    h=re.sub(r'site\.js\?v=[0-9-]+','site.js?v=20260920-56',h)
    p.write_text(h,encoding='utf-8')
