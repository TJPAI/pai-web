from pathlib import Path
import re

# Increase per-glyph angular spacing while keeping the accepted orbit size/position.
p = Path('assets/js/site.js')
s = p.read_text(encoding='utf-8')
old = """        const charStep=ascii
          ? (chars.length<=4?4.2:Math.min(3,22/Math.max(1,chars.length-1)))
          : 5.4;"""
new = """        const charStep=ascii
          ? (chars.length<=4?5.4:Math.min(4.2,36/Math.max(1,chars.length-1)))
          : (chars.length<=2?8.2:8.8);"""
if old not in s:
    raise SystemExit('charStep block not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

# Slightly smaller glyph box + slightly larger text radius; visual circle itself is unchanged.
p = Path('assets/css/app-core.css')
s = p.read_text(encoding='utf-8')
old_css = '.pai-orbit-char{position:absolute;left:50%;top:50%;width:1.25em;height:1.25em;margin:-.625em 0 0 -.625em;display:flex;align-items:center;justify-content:center;color:#171A1F;font-size:11.5px;font-weight:620;line-height:1;letter-spacing:0;transform:rotate(var(--char-angle)) translateY(calc(var(--orbit-size)*-.395));transform-origin:50% 50%;pointer-events:none;user-select:none;-webkit-user-select:none;z-index:3}'
new_css = '.pai-orbit-char{position:absolute;left:50%;top:50%;width:1.05em;height:1.2em;margin:-.6em 0 0 -.525em;display:flex;align-items:center;justify-content:center;color:#171A1F;font-size:11.2px;font-weight:620;line-height:1;letter-spacing:0;transform:rotate(var(--char-angle)) translateY(calc(var(--orbit-size)*-.415));transform-origin:50% 50%;pointer-events:none;user-select:none;-webkit-user-select:none;z-index:3}'
if old_css not in s:
    raise SystemExit('orbit char css not found')
s = s.replace(old_css, new_css, 1)
p.write_text(s, encoding='utf-8')

# Cache-bust both CSS and JS.
p = Path('assets/css/refine.css')
s = p.read_text(encoding='utf-8')
s = s.replace('./app-core.css?v=20260920-20','./app-core.css?v=20260920-21')
p.write_text(s, encoding='utf-8')

for html in Path('.').rglob('*.html'):
    s = html.read_text(encoding='utf-8')
    s = re.sub(r'refine\.css\?v=[^\"\']+', 'refine.css?v=20260920-21', s)
    s = re.sub(r'site\.js\?v=[^\"\']+', 'site.js?v=20260920-62', s)
    html.write_text(s, encoding='utf-8')
