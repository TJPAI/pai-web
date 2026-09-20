from pathlib import Path
import re

p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old="""    const menuData=()=>{\n      const en=normalizedPath().startsWith('/en/');\n      const lang=en?'en':'zh';\n      const languageLabel=en?'中文':'EN';\n      return [...navItems(lang),[languageLabel,counterpartWithContext(normalizedPath())]];\n    };\n"""
new="""    const menuData=()=>{\n      const en=normalizedPath().startsWith('/en/');\n      const lang=en?'en':'zh';\n      const languageLabel=en?'中文':'EN';\n      const home=[en?'Home':'首页',en?'/en/':'/'];\n      return [home,...navItems(lang),[languageLabel,counterpartWithContext(normalizedPath())]];\n    };\n"""
if old not in s:
    raise SystemExit('menuData block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

for html in Path('.').rglob('*.html'):
    h=html.read_text(encoding='utf-8')
    h=re.sub(r'site\\.js\\?v=[0-9-]+','site.js?v=20260920-59',h)
    html.write_text(h,encoding='utf-8')
