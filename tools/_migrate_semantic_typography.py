#!/usr/bin/env python3
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def add_class(attrs, cls):
    m=re.search(r'class="([^"]*)"',attrs)
    if m:
        classes=m.group(1).split()
        if cls not in classes:
            classes.append(cls)
        return attrs[:m.start()]+f'class="{" ".join(classes)}"'+attrs[m.end():]
    return attrs+f' class="{cls}"'


def mark_first_heading(block, tag, cls):
    pat=re.compile(rf'<{tag}([^>]*)>',re.I)
    m=pat.search(block)
    if not m:
        return block
    attrs=add_class(m.group(1),cls)
    return block[:m.start()]+f'<{tag}{attrs}>'+block[m.end():]


def mark_blocks(text, block_pattern, tag, cls):
    pat=re.compile(block_pattern,re.I|re.S)
    return pat.sub(lambda m: mark_first_heading(m.group(0),tag,cls),text)

for path in ROOT.rglob('*.html'):
    rel=path.relative_to(ROOT)
    # Generated/browser fallback pages are not part of the canonical content hierarchy.
    if str(rel)=='404.html':
        continue
    text=path.read_text(encoding='utf-8')
    before=text

    # Display title: homepage only.
    text=mark_blocks(text,r'<section\b[^>]*class="[^"]*\bhome-hero\b[^"]*"[^>]*>.*?</section>','h1','title-display')

    # Page title and major section titles.
    text=mark_blocks(text,r'<section\b[^>]*class="[^"]*\bpage-hero\b[^"]*"[^>]*>.*?</section>','h1','title-page')
    text=mark_blocks(text,r'<div\b[^>]*class="[^"]*\bsection-head\b[^"]*"[^>]*>.*?</div>','h2','title-section')
    text=mark_blocks(text,r'<section\b[^>]*class="[^"]*\bjoin\b[^"]*"[^>]*>.*?</section>','h2','title-section')
    # Some legacy section headings use eyebrow + h2 without section-head wrapper.
    text=re.sub(r'(<div class="eyebrow">[^<]*</div>)<h2([^>]*)>',
                lambda m:m.group(1)+'<h2'+add_class(m.group(2),'title-section')+'>',text)

    # Featured subsection titles.
    text=re.sub(r'<h3([^>]*class="[^"]*\bresearch-title\b[^"]*"[^>]*)>',
                lambda m:'<h3'+add_class(m.group(1),'title-feature')+'>',text)
    text=mark_blocks(text,r'<section\b[^>]*class="[^"]*\bresearch-direction\b[^"]*"[^>]*>.*?</section>','h2','title-feature')
    text=mark_blocks(text,r'<div\b[^>]*class="[^"]*\bperson-detail\b[^"]*"[^>]*>.*?</div>','h2','title-feature')
    # Remaining prose h2 elements are featured subsection headings unless already classified.
    def prose_repl(m):
        block=m.group(0)
        def h2_repl(h):
            attrs=h.group(1)
            if 'title-section' in attrs or 'title-feature' in attrs:
                return h.group(0)
            return '<h2'+add_class(attrs,'title-feature')+'>'
        return re.sub(r'<h2([^>]*)>',h2_repl,block,flags=re.I)
    text=re.sub(r'<div\b[^>]*class="[^"]*\bprose\b[^"]*"[^>]*>.*?</div>',prose_repl,text,flags=re.I|re.S)

    # Item/card/list titles.
    for token in ('challenge','person','highlight','partner','join-item','contact-card'):
        text=mark_blocks(text,rf'<(?:article|div)\b[^>]*class="[^"]*\b{re.escape(token)}\b[^"]*"[^>]*>.*?</(?:article|div)>','h3','title-item')

    # International/platform detail blocks are items, except faculty detail blocks which are minor headings.
    def detail_repl(m):
        block=m.group(0)
        # person-detail ancestors are handled below; this fallback is item-level.
        return mark_first_heading(block,'h3','title-item')
    text=re.sub(r'<div\b[^>]*class="[^"]*\bdetail-block\b[^"]*"[^>]*>.*?</div>',detail_repl,text,flags=re.I|re.S)

    # Faculty detail blocks use the minor title level. Replace title-item if previously added.
    def person_detail_repl(m):
        block=m.group(0)
        block=mark_first_heading(block,'h2','title-feature')
        def db(dm):
            b=dm.group(0)
            hm=re.search(r'<h3([^>]*)>',b,re.I)
            if not hm: return b
            attrs=hm.group(1).replace(' title-item','').replace('title-item ','').replace('title-item','')
            attrs=add_class(attrs,'title-minor')
            return b[:hm.start()]+'<h3'+attrs+'>'+b[hm.end():]
        return re.sub(r'<div\b[^>]*class="[^"]*\bdetail-block\b[^"]*"[^>]*>.*?</div>',db,block,flags=re.I|re.S)
    text=re.sub(r'<div\b[^>]*class="[^"]*\bperson-detail\b[^"]*"[^>]*>.*?</(?:section|div)>',person_detail_repl,text,flags=re.I|re.S)

    # Indexed rows: same typographic level as their item titles, visually de-emphasized.
    def index_block_repl(m):
        block=m.group(0)
        return re.sub(r'<div([^>]*class="[^"]*\bnum\b[^"]*"[^>]*)>',
                      lambda n:'<div'+add_class(n.group(1),'item-index')+'>',block,count=1,flags=re.I)
    for token in ('challenge','highlight','join-item'):
        text=re.sub(rf'<(?:article|div)\b[^>]*class="[^"]*\b{re.escape(token)}\b[^"]*"[^>]*>.*?</(?:article|div)>',index_block_repl,text,flags=re.I|re.S)

    if text!=before:
        path.write_text(text,encoding='utf-8')
        print('updated',rel)

# Semantic classes become first-class selectors, with structural selectors retained as compatibility aliases.
tp=ROOT/'assets/css/typography.css'
t=tp.read_text(encoding='utf-8')
replacements={
    '.home-hero h1{':'.title-display,.home-hero h1{',
    '.page-hero h1{':'.title-page,.page-hero h1{',
    '.section-head h2,.join h2{':'.title-section,.section-head h2,.join h2{',
    '.prose h2,.research-direction h2,.research h3,.research-title,.impact h3,.person-detail h2{':'.title-feature,.prose h2,.research-direction h2,.research h3,.research-title,.impact h3,.person-detail h2{',
    '.challenge h3,#collaboration .partner h3,#achievements .highlight h3,#international-impact .detail-block h3,.join-item h3,.team-grid .person h3,.pub h3,.news-row h3,.contact-card h3{':'.title-item,.challenge h3,#collaboration .partner h3,#achievements .highlight h3,#international-impact .detail-block h3,.join-item h3,.team-grid .person h3,.pub h3,.news-row h3,.contact-card h3{',
    '#achievements .highlight .num,.challenge .num,.join-item .num{':'.item-index,#achievements .highlight .num,.challenge .num,.join-item .num{',
    '.person-detail .detail-block h3{':'.title-minor,.person-detail .detail-block h3{'
}
for old,new in replacements.items():
    if old in t and new not in t:
        t=t.replace(old,new,1)
tp.write_text(t,encoding='utf-8')

# Dynamic publication titles use the same semantic item-title class.
js=ROOT/'assets/js/site.js'
s=js.read_text(encoding='utf-8')
s=s.replace('article.innerHTML=`<h3>${esc(publication.title)}</h3>',
            'article.innerHTML=`<h3 class="title-item">${esc(publication.title)}</h3>')
js.write_text(s,encoding='utf-8')

# Validation: semantic hierarchy is now part of the content contract.
vp=ROOT/'tools/validate.py'
v=vp.read_text(encoding='utf-8')
v=v.replace("if home.count('class=\"research-title\"')!=3: errors.append(f'{prefix}index.html: expected exactly 3 canonical research-title elements')",
            "if len(re.findall(r'class=\"[^\"]*\\bresearch-title\\b[^\"]*\"',home))!=3: errors.append(f'{prefix}index.html: expected exactly 3 canonical research-title elements')")
v=v.replace("if detail.count('class=\"research-title\"')!=3: errors.append(f'{prefix}research.html: expected exactly 3 canonical research-title elements')",
            "if len(re.findall(r'class=\"[^\"]*\\bresearch-title\\b[^\"]*\"',detail))!=3: errors.append(f'{prefix}research.html: expected exactly 3 canonical research-title elements')")
marker='# Semantic title hierarchy guardrail.'
if marker not in v:
    guard=r'''

# Semantic title hierarchy guardrail.
# Structural selectors remain compatibility aliases, but canonical content must declare its title level explicitly.
for html in html_files:
    rel=str(html.relative_to(ROOT))
    if rel=='404.html':
        continue
    text=html_text[html.resolve()]
    for block in re.findall(r'<section\b[^>]*class=["\'][^"\']*\bpage-hero\b[^"\']*["\'][^>]*>.*?</section>',text,re.I|re.S):
        m=re.search(r'<h1\b([^>]*)>',block,re.I)
        if m and not re.search(r'\btitle-page\b',m.group(1)):
            errors.append(f'{rel}: page-hero h1 must declare title-page')
    for block in re.findall(r'<div\b[^>]*class=["\'][^"\']*\bsection-head\b[^"\']*["\'][^>]*>.*?</div>',text,re.I|re.S):
        m=re.search(r'<h2\b([^>]*)>',block,re.I)
        if m and not re.search(r'\btitle-section\b',m.group(1)):
            errors.append(f'{rel}: section-head h2 must declare title-section')
    for m in re.finditer(r'<h3\b([^>]*)class=["\'][^"\']*\bresearch-title\b[^"\']*["\'][^>]*>',text,re.I):
        if 'title-feature' not in m.group(0):
            errors.append(f'{rel}: research-title must also declare title-feature')

for required in ('.title-display','.title-page','.title-section','.title-feature','.title-item','.title-minor','.item-index'):
    if required not in _typography:
        errors.append(f'assets/css/typography.css: missing semantic title class {required}')
if '<h3 class="title-item">${esc(publication.title)}</h3>' not in site_js:
    errors.append('assets/js/site.js: publication titles must use semantic title-item class')
'''
    anchor='if errors:\n'
    pos=v.rfind(anchor)
    if pos!=-1:
        v=v[:pos]+guard+'\n'+v[pos:]
    else:
        v+=guard
vp.write_text(v,encoding='utf-8')
