from pathlib import Path
import subprocess
import re

# Restore site.js from the last known-good main before the accidental whole-file overwrite.
old = subprocess.check_output([
    'git','show','f55b7df09cfabd140d899ae31372c55cb4eefb00:assets/js/site.js'
], text=True)

s = old
old_arc = """  const arcPath=(angle,index)=>{\n    const r=82,half=16;\n    let a1=angle-half,a2=angle+half,sweep=1;\n    const norm=((angle%360)+360)%360;\n    if(norm>90&&norm<270){const t=a1;a1=a2;a2=t;sweep=0;}\n    const p1=polar(110,110,r,a1),p2=polar(110,110,r,a2);\n    return `M ${p1[0].toFixed(2)} ${p1[1].toFixed(2)} A ${r} ${r} 0 0 ${sweep} ${p2[0].toFixed(2)} ${p2[1].toFixed(2)}`;\n  };"""
new_arc = """  const arcPath=angle=>{\n    const r=82,half=16;\n    const a1=angle-half,a2=angle+half;\n    const p1=polar(110,110,r,a1),p2=polar(110,110,r,a2);\n    return `M ${p1[0].toFixed(2)} ${p1[1].toFixed(2)} A ${r} ${r} 0 0 1 ${p2[0].toFixed(2)} ${p2[1].toFixed(2)}`;\n  };"""
if old_arc not in s:
    raise SystemExit('arcPath block not found')
s = s.replace(old_arc, new_arc, 1)

# Paths are fixed in the wheel coordinate system. The wheel itself is the only thing that rotates.
s = s.replace(
    "const defs=data.map((_,i)=>`<path id=\"orbit-arc-${i}\" d=\"${arcPath(i*45+rotation,i)}\"/>`).join('');",
    "const defs=data.map((_,i)=>`<path id=\"orbit-arc-${i}\" d=\"${arcPath(i*45)}\"/>`).join('');",
    1,
)

Path('assets/js/site.js').write_text(s, encoding='utf-8')

# Bump only the JS cache key across HTML pages.
for p in Path('.').rglob('*.html'):
    h = p.read_text(encoding='utf-8')
    h = re.sub(r'site\\.js\\?v=[0-9-]+', 'site.js?v=20260920-55', h)
    p.write_text(h, encoding='utf-8')
