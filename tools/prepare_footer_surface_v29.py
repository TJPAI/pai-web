from pathlib import Path
p=Path('tools/make_footer_page_surface_v29.py')
s=p.read_text()
old="""'''    const current=document.querySelector('main');\\n    if(current){\\n      current.style.willChange='transform';\\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\\n    }\\n    if(!preview) return;\\n    const direction=preview.direction;\\n    if((direction>0&&bounded>0)||(direction<0&&bounded<0)) return;\\n    const incoming=bounded+(direction>0?width:-width);\\n    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;\\n''',"""
new="""'''    const direction=bounded<0?1:-1;\\n    const current=document.querySelector('main');\\n    if(current){\\n      current.style.willChange='transform';\\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\\n    }\\n    const preview=swipePreview;\\n    if(!preview||preview.direction!==direction) return;\\n    const incoming=bounded+(direction>0?width:-width);\\n    preview.main.style.transform=`translate3d(${incoming}px,0,0)`;\\n''',"""
if old not in s:
    raise SystemExit('migration position source block not found')
s=s.replace(old,new,1)
old2="""'''    const current=document.querySelector('.page-surface');\\n    if(current){\\n      current.style.willChange='transform';\\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\\n    }\\n    if(!preview) return;\\n    const direction=preview.direction;\\n    if((direction>0&&bounded>0)||(direction<0&&bounded<0)) return;\\n    const incoming=bounded+(direction>0?width:-width);\\n    preview.surface.style.transform=`translate3d(${incoming}px,0,0)`;\\n''',"""
new2="""'''    const direction=bounded<0?1:-1;\\n    const current=document.querySelector('.page-surface');\\n    if(current){\\n      current.style.willChange='transform';\\n      current.style.transform=`translate3d(${bounded}px,0,0)`;\\n    }\\n    const preview=swipePreview;\\n    if(!preview||preview.direction!==direction) return;\\n    const incoming=bounded+(direction>0?width:-width);\\n    preview.surface.style.transform=`translate3d(${incoming}px,0,0)`;\\n''',"""
if old2 not in s:
    raise SystemExit('migration position destination block not found')
s=s.replace(old2,new2,1)
p.write_text(s)
print('aligned migration script with v28 deterministic swipe')
