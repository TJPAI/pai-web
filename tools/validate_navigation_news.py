#!/usr/bin/env python3
"""Static acceptance for regular menu hints and bilingual Latest News."""
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
js=(ROOT/'assets/js/site.js').read_text()
css=(ROOT/'assets/css/refine.css').read_text()
assert "link.querySelectorAll('.nav-updates-hint')" in js, "Existing static header links must receive the news hint"
assert "hint.textContent=lang==='en'?'(latest updates)':'（最新动态）'" in js
assert "for(const selector of ['.nav-links','.mobile-menu'])" in js, "Destination static menus must be copied when navigating"
assert ".site-header .nav-updates-hint" in css
assert "results-news-toggle" in js and "extra.hidden=!open" in js
class NewsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_news=False;self.level=0;self.in_list=False;self.extra=False
        self.counts=[0,0];self.dates=[[],[]];self.terms=[]
    def handle_starttag(self,tag,attrs):
        attr=dict(attrs); classes=attr.get('class','').split()
        if tag=='aside' and 'results-news' in classes:
            self.in_news=True;self.level=1;return
        if not self.in_news:return
        if tag=='div' and 'results-news-list' in classes:
            self.in_list=True;self.extra='results-news-extra' in classes
            if self.extra:assert 'hidden' in attr
        if self.in_list and 'results-news-row' in classes:self.counts[int(self.extra)]+=1
        if self.in_list and tag=='time':self.dates[int(self.extra)].append(attr.get('datetime'))
    def handle_endtag(self,tag):
        if not self.in_news:return
        if tag=='aside':self.in_news=False
        if tag=='div' and self.in_list:
            pass
for path in ('publications.html','en/publications.html'):
    html=(ROOT/path).read_text()
    start=html.index('<aside class="results-news"')
    end=html.index('</aside>',start)+len('</aside>')
    pane=html[start:end]
    a=pane.split('<div class="results-news-list results-news-extra"')
    assert len(a)==2
    assert a[0].count('class="results-news-row')==5,(path,'default rows')
    assert a[1].count('class="results-news-row')==40,(path,'extra rows')
    assert pane.index('aria-expanded="false"')<pane.index('results-news-extra')
    assert '2026-09' in a[0] and '2026-05' in a[0]
    assert ('(latest updates)' if path.startswith('en/') else '（最新动态）') in js
    if path.startswith('en/'):
        assert 'High-Level Expert Panel' in a[0]
        assert 'High-Level Expert Group' not in pane
        assert 'successful large-scale mine trials.' in html
    else:
        assert '和IET首席执行官Nigel Fine共同宣布' not in pane
        assert '《IET Blockchain》期刊正式启动' in pane
print('PASS: regular navigation and bilingual Latest News static contracts')

# Guard the shared two-line footer brand and editorial news wording.
from pathlib import Path as _Path
for _page in list(_Path('.').glob('*.html')) + list(_Path('en').glob('*.html')) + list(_Path('people').glob('*.html')) + list(_Path('en/people').glob('*.html')):
    _html = _page.read_text(encoding='utf-8')
    if '<footer ' in _html:
        assert '<strong>PAI Research Center</strong><span>Tongji University</span>' in _html, (_page, 'footer brand')
for _page in ('publications.html', 'en/publications.html'):
    _html = _Path(_page).read_text(encoding='utf-8')
    assert 'DWELT定位项目获' not in _html and 'DWELT localization project wins' not in _html
    assert ('DWELT technology wins gold' if _page.startswith('en/') else 'DWELT技术获') in _html
    _news = _html.split('<aside class="results-news"', 1)[1].split('</aside>', 1)[0]
    assert _news.count('https://doi.org/') >= 24
    assert ('等论文发表于' if not _page.startswith('en/') else '— TWC paper published') not in _news

_js = _Path('assets/js/site.js').read_text(encoding='utf-8')
assert "footer.innerHTML=" not in _js, 'Runtime must not regenerate footer HTML'
assert "currentFooter.replaceWith(incomingFooter)" in _js, 'Lightweight navigation must swap the destination footer'
assert "targetFooter=next.querySelector('.site-footer')" in _js, 'Destination footer must come from destination HTML'
assert '<div class="brand"><strong>PAI</strong><span>PAI Research Center · Tongji University</span></div>' not in _js, 'Runtime must not contain stale footer branding'

assert "nav.innerHTML=markup" not in _js, 'Runtime must not regenerate static desktop navigation'
assert "mobile.innerHTML=markup" not in _js, 'Runtime must not regenerate static mobile navigation'
assert "link.setAttribute('href',target.getAttribute('href'))" in _js, 'Header links must sync without replacing navigation DOM'

# Canonical news records must produce the exact committed bilingual HTML.
import subprocess as _subprocess
import sys as _sys
_subprocess.run([_sys.executable, str(_Path('tools/render_latest_news.py')), '--check'], check=True)

assert 'const navItems=lang' not in _js, 'Orbit must not maintain a second translated menu list'
assert "document.querySelectorAll('.site-header .nav-links a')" in _js, 'Orbit navigation must use source-page header links'

# Footer order must agree across the bilingual site: brand, links, contact.
for _page in list(_Path('.').glob('*.html')) + list(_Path('en').glob('*.html')):
    _html = _page.read_text(encoding='utf-8')
    if '<footer ' not in _html:
        continue
    _footer = _html.split('<footer ', 1)[1].split('</footer>', 1)[0]
    if 'class="footer-links"' in _footer and 'class="footer-contact"' in _footer:
        assert _footer.index('class="footer-links"') < _footer.index('class="footer-contact"'), (_page, 'menu must precede address')
        assert _footer.index('class="footer-contact"') > _footer.index('class="footer-links"'), (_page, 'footer column order')

# Collaboration platform targets and homepage footer consistency.
for _page, _gbc in (('index.html', 'https://ieee-gbc.org.cn/'), ('en/index.html', 'https://ieee-gbc.org/')):
    _html = _Path(_page).read_text(encoding='utf-8')
    for _url in ('https://ietresearch.onlinelibrary.wiley.com/journal/26341573', _gbc, 'https://blockchain.ieee.org/'):
        assert f'href="{_url}"' in _html, (_page, _url)
    _footer = _html.split('<footer ', 1)[1].split('</footer>', 1)[0]
    assert 'class="footer-meta"' in _footer, (_page, 'copyright row')
    assert 'class="footer-contact"' in _footer and 'lingtang@tongji.edu.cn' in _footer, (_page, 'footer contact')
    assert _footer.index('class="footer-links"') < _footer.index('class="footer-contact"'), (_page, 'footer order')

# Safari must not retain compositor transforms after a lightweight page transition.
assert 'animation?.cancel()' in _js, 'Lightweight page animation must release its fill layer'
assert "incomingFooter.style.transform=''" in _js, 'Replacement footer must not carry swipe transforms'

# Footer menu is identical on every primary page within each language.
import re as _re
for _prefix, _names in (
    ('', ['关于我们','研究团队','研究方向','成果合作','加入我们','联系我们','EN']),
    ('en/', ['About','People','Research','Outputs','Join','Contact','中文']),
):
    for _name in ('index.html','about.html','team.html','research.html','publications.html','join.html','contact.html'):
        _page = _Path(_prefix + _name)
        _source = _page.read_text(encoding='utf-8')
        _footer = _source.split('<footer ',1)[1].split('</footer>',1)[0]
        _links = _footer.split('<div class="footer-links">',1)[1].split('</div>',1)[0]
        _labels = _re.findall(r'<a[^>]*>(.*?)</a>',_links)
        assert _labels == _names, (_page, _labels, _names)
        assert _footer.index('class="footer-links"') < _footer.index('class="footer-contact"'), _page

assert 'from.innerHTML=to.innerHTML' not in _js, 'Header DOM must not be rebuilt on route changes'

# SPA header reconciliation must not incorporate rendered news hints into base text.
assert "target.childNodes[0]?.textContent" in _js, 'Header label must ignore updates hint children'
assert "hints.forEach(node=>node.remove())" in _js, 'Old navigation hint nodes must be cleared on route transition'
assert "hints.slice(1).forEach(node=>node.remove())" in _js, 'Navigation hint must not duplicate'
