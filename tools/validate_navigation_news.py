#!/usr/bin/env python3
"""Static acceptance for regular menu hints and bilingual Latest News."""
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
js=(ROOT/'assets/js/site.js').read_text()
css=(ROOT/'assets/css/refine.css').read_text()
assert "link.querySelector('.nav-updates-hint')" in js, "Existing static header links must receive the news hint"
assert "hint.textContent=lang==='en'?'(latest updates)':'（最新动态）'" in js
assert "const displayLabel=key==='publications'" in js, "Rebuilt menus must also include hint"
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
assert '<div class="brand"><strong>PAI Research Center</strong><span>Tongji University</span></div>' in _js, 'Runtime footer must match static two-line brand'
assert '<div class="brand"><strong>PAI</strong><span>PAI Research Center · Tongji University</span></div>' not in _js, 'Runtime footer must not restore stale branding'
