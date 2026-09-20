from pathlib import Path
import re

p=Path('assets/js/site.js')
s=p.read_text(encoding='utf-8')
old="""    const menuData=()=>{\n      const en=normalizedPath().startsWith('/en/');\n      return en?[\n        ['Home','/en/'],['About','/en/about.html'],['People','/en/team.html'],['Research','/en/research.html'],\n        ['Publications','/en/publications.html'],['Join','/en/join.html'],['Contact','/en/contact.html'],['中文',counterpartWithContext(normalizedPath())]\n      ]:[\n        ['首页','/'],['关于','/about.html'],['团队','/team.html'],['研究','/research.html'],\n        ['成果','/publications.html'],['加入','/join.html'],['联系','/contact.html'],['EN',counterpartWithContext(normalizedPath())]\n      ];\n    };\n\n    const sync=()=>{\n      const en=normalizedPath().startsWith('/en/');\n      const data=menuData();\n      wheel.innerHTML=data.map(([label,href],i)=>\n        `<a class=\"pai-orbit-item\" href=\"${root(href)}\" style=\"--item-angle:${i*45}deg\"><span>${label}</span></a>`\n      ).join('');\n"""
new="""    const menuData=()=>{\n      const en=normalizedPath().startsWith('/en/');\n      const lang=en?'en':'zh';\n      const languageLabel=en?'中文':'EN';\n      return [...navItems(lang),[languageLabel,counterpartWithContext(normalizedPath())]];\n    };\n\n    const sync=()=>{\n      const en=normalizedPath().startsWith('/en/');\n      const data=menuData();\n      const step=360/data.length;\n      wheel.innerHTML=data.map(([label,href],i)=>\n        `<a class=\"pai-orbit-item\" href=\"${root(href)}\" style=\"--item-angle:${i*step}deg\"><span>${label}</span></a>`\n      ).join('');\n"""
if old not in s:
    raise SystemExit('orbit menu block not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

for html in Path('.').rglob('*.html'):
    h=html.read_text(encoding='utf-8')
    h=re.sub(r'site\\.js\\?v=[0-9-]+','site.js?v=20260920-58',h)
    html.write_text(h,encoding='utf-8')
