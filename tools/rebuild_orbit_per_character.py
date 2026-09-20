from pathlib import Path
import re

# site.js: render each visible glyph as its own circular element while keeping
# one ordinary anchor per menu item for navigation/click semantics.
p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old=re.compile(r"    const sync=\(\)=>\{\n      const en=normalizedPath\(\)\.startsWith\('/en/'\);\n      const data=menuData\(\);\n      const step=360/data\.length;\n      wheel\.innerHTML=data\.map\(\(\[label,href\],i\)=>\n        `<a class=\"pai-orbit-item\" href=\"\$\{root\(href\)\}\" style=\"--item-angle:\$\{i\*step\}deg\"><span>\$\{label\}</span></a>`\n      \)\.join\(''\);\n      wheel\.setAttribute\('aria-label',en\?'Quick navigation':'快捷导航'\);\n      toggle\.setAttribute\('aria-label',orbit\.classList\.contains\('open'\)\?\(en\?'Close quick menu':'关闭快捷菜单'\):\(en\?'Open quick menu':'打开快捷菜单'\)\);\n    \};")
new="""    const sync=()=>{\n      const en=normalizedPath().startsWith('/en/');\n      const data=menuData();\n      const step=360/data.length;\n      const markup=[];\n      data.forEach(([label,href],i)=>{\n        const center=i*step;\n        const chars=Array.from(label);\n        const ascii=chars.every(ch=>/[\\x00-\\x7F]/.test(ch));\n        const charStep=ascii\n          ? (chars.length<=4?4.2:Math.min(3,22/Math.max(1,chars.length-1)))\n          : 5.4;\n        markup.push(`<a class=\"pai-orbit-item\" aria-label=\"${label}\" href=\"${root(href)}\" style=\"--item-angle:${center}deg\"><span class=\"pai-orbit-sr\">${label}</span></a>`);\n        chars.forEach((ch,j)=>{\n          const offset=(j-(chars.length-1)/2)*charStep;\n          markup.push(`<span class=\"pai-orbit-char\" aria-hidden=\"true\" style=\"--char-angle:${center+offset}deg\">${ch}</span>`);\n        });\n      });\n      wheel.innerHTML=markup.join('');\n      wheel.setAttribute('aria-label',en?'Quick navigation':'快捷导航');\n      toggle.setAttribute('aria-label',orbit.classList.contains('open')?(en?'Close quick menu':'关闭快捷菜单'):(en?'Open quick menu':'打开快捷菜单'));\n    };"""
s2,n=old.subn(lambda _m:new,s,count=1)
if n!=1:
    raise SystemExit(f'sync block replacement count={n}')
p.write_text(s2,encoding='utf-8')

# app-core.css: invisible hit anchors + individually positioned visible glyphs.
p=Path('assets/css/app-core.css')
s=p.read_text(encoding='utf-8')
old_css=re.compile(r"\.pai-orbit-item\{[^}]*\}\n\.pai-orbit-item span\{[^}]*\}")
new_css=""".pai-orbit-item{position:absolute;left:50%;top:50%;width:76px;height:38px;margin:-19px 0 0 -38px;display:block;color:#171A1F;text-decoration:none;transform:rotate(var(--item-angle)) translateY(calc(var(--orbit-size)*-.395));transform-origin:50% 50%;-webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none;z-index:2}\n.pai-orbit-sr{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}\n.pai-orbit-char{position:absolute;left:50%;top:50%;width:1.25em;height:1.25em;margin:-.625em 0 0 -.625em;display:flex;align-items:center;justify-content:center;color:#171A1F;font-size:11.5px;font-weight:620;line-height:1;letter-spacing:0;transform:rotate(var(--char-angle)) translateY(calc(var(--orbit-size)*-.395));transform-origin:50% 50%;pointer-events:none;user-select:none;-webkit-user-select:none;z-index:3}"""
s2,n=old_css.subn(lambda _m:new_css,s,count=1)
if n!=1:
    raise SystemExit(f'orbit css replacement count={n}')
p.write_text(s2,encoding='utf-8')

# Cache-bust both CSS entry and JS runtime correctly.
p=Path('assets/css/refine.css')
s=p.read_text(encoding='utf-8')
s=s.replace('./app-core.css?v=20260920-19','./app-core.css?v=20260920-20')
p.write_text(s,encoding='utf-8')

for html in Path('.').rglob('*.html'):
    s=html.read_text(encoding='utf-8')
    s=re.sub(r'refine\.css\?v=[^\"\']+', 'refine.css?v=20260920-20', s)
    s=re.sub(r'site\.js\?v=[^\"\']+', 'site.js?v=20260920-61', s)
    html.write_text(s,encoding='utf-8')
