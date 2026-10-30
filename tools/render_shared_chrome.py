#!/usr/bin/env python3
"""Single build-time owner for bilingual static Header/Footer across public pages.

Use --check for drift detection; otherwise rewrite source HTML in the build workspace.
No client-side JS templating or network request is necessary.
"""
from pathlib import Path
from html import escape
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]
FILES = ['index.html','about.html','team.html','research.html','publications.html','join.html','contact.html']
PEOPLE = ['erwu-liu','rui-wang','gang-shen','dunhui-xiao','shuyan-hu','yan-liu']
PAGES = FILES + [f'people/{p}.html' for p in PEOPLE]
LABELS = {
    'zh':['关于我们','研究团队','研究方向','成果合作','加入我们','联系我们'],
    'en':['About','People','Research','Outputs','Join','Contact']
}
DESTS = ['about.html','team.html','research.html','publications.html','join.html','contact.html']
ADDRESS = {
    'zh':'上海市嘉定区曹安公路4800号<br>同济大学嘉定校区智信馆',
    'en':"Zhixin Building, Tongji University Jiading Campus<br>4800 Cao'an Highway, Jiading District, Shanghai"
}
HEADER = re.compile(r'<header class="site-header">.*?</header>',re.S)
FOOTER = re.compile(r'<footer class="site-footer[^"]*">.*?</footer>',re.S)

def render(relative,lang):
    directory=relative.parent
    prefix='../' * len(directory.parts)
    # target file is relative to its language-specific top-level directory
    leaf=relative.as_posix()
    if lang=='en':
        actual=Path('en')/relative
        prefix='../' * len(actual.parent.parts)
        navbase=('../' if len(relative.parts)>1 else '')
        counterpart=prefix + leaf
    else:
        actual=relative
        prefix='../' * len(actual.parent.parts)
        navbase=('../' if len(relative.parts)>1 else '')
        counterpart=prefix + 'en/' + leaf
    active='team.html' if leaf.startswith('people/') else relative.name
    navlinks=[]
    mobilenav=[]
    footerlinks=[]
    for name,dest in zip(LABELS[lang],DESTS):
        href=navbase+dest
        activeattr=' class="active" aria-current="page"' if dest==active else ''
        navlinks.append(f'<a{activeattr} href="{href}">{name}</a>')
        mobilenav.append(f'<a href="{href}">{name}</a>')
        footerlinks.append(f'<a href="{href}">{name}</a>')
    switch='中文' if lang=='en' else 'EN'
    navlinks.append(f'<a href="{counterpart}">{switch}</a>')
    mobilenav.append(f'<a href="{counterpart}">{switch}</a>')
    footerlinks.append(f'<a href="{counterpart}">{switch}</a>')
    home=navbase+'index.html'
    hlabel='Main navigation' if lang=='en' else '主导航'
    mlabel='Mobile navigation' if lang=='en' else '移动导航'
    button='Open menu' if lang=='en' else '打开菜单'
    header=(f'<header class="site-header"><div class="container nav"><a class="brand" href="{home}">'
       '<strong>PAI</strong><span>Tongji University</span></a>'
       f'<nav class="nav-links" aria-label="{hlabel}">{"".join(navlinks)}</nav>'
       f'<button class="menu-btn" aria-label="{button}" aria-expanded="false" aria-controls="mobile-navigation">☰</button>'
       f'</div><nav class="mobile-menu" id="mobile-navigation" aria-label="{mlabel}">'
       f'{"".join(mobilenav)}</nav></header>')
    brand_name='PAI Research Center' if lang=='en' else 'PAI研究中心'
    footer=('<footer class="site-footer compact-footer"><div class="container"><div class="footer-grid">'
       f'<div><div class="brand"><strong>{brand_name}</strong><span>Tongji University</span></div></div>'
       f'<div class="footer-links">{"".join(footerlinks)}</div>'
       f'<div class="footer-contact">{ADDRESS[lang]}<br>'
       '<a href="mailto:lingtang@tongji.edu.cn">lingtang@tongji.edu.cn</a></div></div>'
       '<div class="footer-meta"><span>© 2026 PAI Research Center · Tongji University</span></div>'
       '</div></footer>')
    return actual,header,footer

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    changed=[]
    for lang in ('zh','en'):
        for leaf in PAGES:
            path,header,footer=render(Path(leaf),lang)
            file=ROOT/path
            src=file.read_text(encoding='utf-8')
            out,n1=HEADER.subn(lambda _:header,src,count=1)
            out,n2=FOOTER.subn(lambda _:footer,out,count=1)
            if (n1,n2)!=(1,1):
                raise SystemExit(f'{path}: expected exactly one header and footer; found {n1}/{n2}')
            if src!=out:
                if args.check: changed.append(str(path))
                else:
                    file.write_text(out,encoding='utf-8')
                    changed.append(str(path))
    if args.check and changed:
        raise SystemExit('Shared chrome differs from canonical template: '+', '.join(changed))
    print(f'PASS: shared bilingual Header/Footer in {2*len(PAGES)} pages; updated {len(changed)}')

if __name__=='__main__':
    main()
