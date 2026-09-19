#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import unquote
import json, re, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]
all_pubs=[]

# Validate publication data.
for rel in ['data/publications.json','data/publications-archive.json']:
    p=ROOT/rel
    if not p.exists():
        continue
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        errors.append(f'{rel}: invalid JSON: {e}')
        continue
    if not isinstance(data,list):
        errors.append(f'{rel}: root must be an array')
        continue
    for i,item in enumerate(data,1):
        for key in ('year','title','authors','venue'):
            if not item.get(key): errors.append(f'{rel}[{i}]: missing {key}')
        if 'doi' in item and item['doi'] and not str(item['doi']).startswith('10.'):
            errors.append(f'{rel}[{i}]: suspicious DOI {item["doi"]}')
        if item.get('pdf'):
            errors.append(f'{rel}[{i}]: publication PDF links are not maintained in pai-web; use DOI/publisher links')
        all_pubs.append((rel,i,item))

# Detect duplicate titles / DOI assignments across all publication datasets.
def norm_title(value):
    return re.sub(r'\s+',' ',str(value or '').strip().lower())

titles={}
dois={}
for rel,i,item in all_pubs:
    title=norm_title(item.get('title'))
    if title:
        if title in titles:
            prev=titles[title]
            errors.append(f'{rel}[{i}]: duplicate title also in {prev[0]}[{prev[1]}]: {item.get("title")}')
        else:
            titles[title]=(rel,i)
    doi=str(item.get('doi') or '').strip().lower()
    if doi:
        if doi in dois:
            prev=dois[doi]
            errors.append(f'{rel}[{i}]: duplicate DOI {doi} also in {prev[0]}[{prev[1]}')
        else:
            dois[doi]=(rel,i)

html_files=list(ROOT.rglob('*.html'))
html_text={p.resolve():p.read_text(encoding='utf-8') for p in html_files}
html_ids={p:{*re.findall(r'\bid=["\']([^"\']+)["\']',text)} for p,text in html_text.items()}

def hrefs_in_class(text,class_name):
    match=re.search(rf'<(?:nav|div)\b[^>]*class=["\'][^"\']*\b{re.escape(class_name)}\b[^"\']*["\'][^>]*>(.*?)</(?:nav|div)>',text,re.I|re.S)
    if not match:
        return None
    return re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\']',match.group(1),re.I)

# Check local references, fragment targets and common page structure.
for html in html_files:
    text=html_text[html.resolve()]
    rel=str(html.relative_to(ROOT))

    for attr,target in re.findall(r'\b(href|src)=["\']([^"\']+)["\']',text):
        if target.startswith(('http://','https://','mailto:','tel:','data:','javascript:')):
            continue

        raw_path,sep,raw_fragment=target.partition('#')
        path_part=raw_path.split('?',1)[0]
        fragment=unquote(raw_fragment) if sep else ''

        if not path_part:
            resolved=html.resolve()
        else:
            resolved=(html.parent/path_part).resolve()

        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f'{rel}: path escapes site: {target}')
            continue

        if path_part and not resolved.exists():
            errors.append(f'{rel}: missing local {attr}: {path_part}')
            continue

        if fragment:
            target_html=resolved/'index.html' if resolved.is_dir() else resolved
            if target_html.suffix.lower()=='.html':
                target_html=target_html.resolve()
                if target_html not in html_ids:
                    errors.append(f'{rel}: fragment target is not a readable HTML page: {target}')
                elif fragment not in html_ids[target_html]:
                    errors.append(f'{rel}: broken fragment {target}; missing id="{fragment}"')

    if 'class="site-header"' in text:
        for token,name in [
            ('class="nav-links"','desktop nav'),
            ('class="menu-btn"','menu button'),
            ('<main','main'),
            ('class="site-footer','footer'),
            ('assets/js/site.js','shared runtime'),
            ('assets/css/refine.css','shared presentation entry point')
        ]:
            if token not in text:
                errors.append(f'{rel}: missing {name}')

        # Internal implementation styles must only be reached through refine.css.
        if 'assets/css/refine-base.css' in text or 'assets/css/app-core.css' in text:
            errors.append(f'{rel}: internal CSS bundle linked directly; use refine.css only')

        ids=re.findall(r'\bid=["\']([^"\']+)["\']',text)
        duplicates=sorted({value for value in ids if ids.count(value)>1})
        if duplicates:
            errors.append(f'{rel}: duplicate id(s): {", ".join(duplicates)}')

        main_match=re.search(r'<main\b[^>]*>(.*?)</main>',text,re.I|re.S)
        if main_match and re.search(r'<style\b',main_match.group(1),re.I):
            errors.append(f'{rel}: page-local <style> inside <main>; move shared presentation to CSS')

        # All navigation surfaces on a page must lead to the same destinations.
        desktop=hrefs_in_class(text,'nav-links')
        mobile=hrefs_in_class(text,'mobile-menu')
        footer=hrefs_in_class(text,'footer-links')
        if desktop is not None and mobile is not None and set(desktop)!=set(mobile):
            errors.append(f'{rel}: desktop and mobile navigation targets differ')
        if desktop is not None and footer is not None and set(desktop)!=set(footer):
            errors.append(f'{rel}: header and footer navigation targets differ')

    if '高水平科研与代表成果' in text:
        errors.append(f'{rel}: deprecated heading "高水平科研与代表成果"; use "代表性成果"')


# Research identity/title contracts: homepage and detail page must share canonical markup and text.
research_specs=[('01','PNL','Positioning &amp;<br>Localization'),('02','IoT-NG','Internet of Things<br>Next Generation'),('03','AIBI','Artificial Intelligence &amp;<br>Blockchain Intelligence')]
for prefix in ('','en/'):
    home=(ROOT/f'{prefix}index.html').read_text(encoding='utf-8')
    detail=(ROOT/f'{prefix}research.html').read_text(encoding='utf-8')
    for number,code,expansion in research_specs:
        inner=f'<span class="research-index">{number}</span><span class="research-code-main"><span>{code}</span><small class="research-expansion">{expansion}</small></span>'
        if f'<div class="research-code research-identity">{inner}</div>' not in home: errors.append(f'{prefix}index.html: non-canonical research identity for {code}')
        if f'<div class="direction-id research-identity">{inner}</div>' not in detail: errors.append(f'{prefix}research.html: non-canonical research identity for {code}')
    if len(re.findall(r'class="[^"]*\bresearch-title\b[^"]*"',home))!=3: errors.append(f'{prefix}index.html: expected exactly 3 canonical research-title elements')
    if len(re.findall(r'class="[^"]*\bresearch-title\b[^"]*"',detail))!=3: errors.append(f'{prefix}research.html: expected exactly 3 canonical research-title elements')

# Critical detail-link contracts: these links must land on the matching content block, not just the top of a page.
contracts={
    'index.html':[
        'research.html#pnl','research.html#iotng','research.html#aibi',
        'about.html#achievements','contact.html#cooperation'
    ],
    'en/index.html':[
        'research.html#pnl','research.html#iotng','research.html#aibi',
        'about.html#achievements'
    ],
    'join.html':['contact.html#recruitment'],
    'en/join.html':['contact.html#recruitment']
}
for rel,targets in contracts.items():
    text=(ROOT/rel).read_text(encoding='utf-8')
    for target in targets:
        if f'href="{target}"' not in text and f"href='{target}'" not in text:
            errors.append(f'{rel}: expected detail link missing: {target}')

# Anchors intentionally preserved by the language switch must exist in both languages.
shared_context_anchors={
    'about.html':['about','overview','collaboration','achievements','international-impact'],
    'research.html':['pnl','iotng','aibi'],
    'contact.html':['cooperation','recruitment']
}
for rel,anchors in shared_context_anchors.items():
    zh=(ROOT/rel).resolve()
    en=(ROOT/'en'/rel).resolve()
    zh_ids=html_ids.get(zh,set())
    en_ids=html_ids.get(en,set())
    for anchor in anchors:
        if anchor not in zh_ids:
            errors.append(f'{rel}: missing bilingual context anchor id="{anchor}"')
        if anchor not in en_ids:
            errors.append(f'en/{rel}: missing bilingual context anchor id="{anchor}"')

# Chinese/English page pairs should stay complete.
paired=[
    'index.html','about.html','research.html','team.html','publications.html','join.html','contact.html',
    'people/erwu-liu.html','people/rui-wang.html','people/gang-shen.html','people/dunhui-xiao.html','people/shuyan-hu.html','people/yan-liu.html'
]
for rel in paired:
    en_rel='en/'+rel
    if not (ROOT/rel).exists(): errors.append(f'missing Chinese page: {rel}')
    if not (ROOT/en_rel).exists(): errors.append(f'missing English page: {en_rel}')

# English pages must not contain Chinese copy except the intentional language-switch label.
for html in (ROOT/'en').rglob('html'):
    text=html.read_text(encoding='utf-8')
    checked=text.replace('>中文<','><')
    if re.search(r'[\u4e00-\u9fff]',checked):
        errors.append(str(html.relative_to(ROOT))+': unexpected Chinese text in English page')

# Architectural guardrails: one behavior runtime and one deterministic presentation entry point.
site_js=(ROOT/'assets/js/site.js').read_text(encoding='utf-8')
for banned,reason in [
    ('stopImmediatePropagation','event handlers should not suppress unrelated handlers'),
    ('caches.keys(','page runtime must not select Service Worker caches directly'),
    ('installSharedStyles','runtime CSS injection is not allowed')
]:
    if banned in site_js:
        errors.append(f'assets/js/site.js: {reason} ({banned})')
if 'counterpartWithContext' not in site_js:
    errors.append('assets/js/site.js: bilingual navigation must preserve supported detail context')
if 'document.documentElement.lang=next.documentElement.lang' not in site_js:
    errors.append('assets/js/site.js: lightweight navigation must synchronize document language')

refine_css=(ROOT/'assets/css/refine.css').read_text(encoding='utf-8')
for import_name in ('./refine-base.css','./app-core.css'):
    if import_name not in refine_css:
        errors.append(f'assets/css/refine.css: missing shared import {import_name}')
if any(token in refine_css for token in ('.menu-btn{','.research-direction .direction-id{','.team-grid img.person-photo{')):
    errors.append('assets/css/refine.css: entry point should only compose shared style layers, not duplicate component rules')

for shim in ('assets/css/app.css','assets/css/team.css'):
    p=ROOT/shim
    if not p.exists():
        errors.append(f'{shim}: missing compatibility shim')
    elif 'Compatibility shim' not in p.read_text(encoding='utf-8'):
        errors.append(f'{shim}: must remain a compatibility shim; shared rules belong in app-core.css')

for required in ('assets/css/refine-base.css','assets/css/app-core.css'):
    if not (ROOT/required).exists():
        errors.append(f'{required}: missing shared style layer')


# Lightweight-navigation reliability guardrail.
site_js=(ROOT/'assets/js/site.js').read_text(encoding='utf-8')
for required in ('history.pushState','popstate','DOMParser','currentMain.replaceWith','eligiblePageLink'):
    if required not in site_js:
        errors.append(f'assets/js/site.js: lightweight navigation contract missing ({required})')
if "fetch(key,{credentials:'same-origin'})" not in site_js:
    errors.append('assets/js/site.js: lightweight navigation must use ordinary HTTP caching')

# Faculty portraits are ordinary static files. Gang Shen intentionally uses PNG.
portrait_ext={'gang-shen':'png'}
for name in ('erwu-liu','rui-wang','gang-shen','dunhui-xiao','shuyan-hu','yan-liu'):
    ext=portrait_ext.get(name,'jpg')
    rel=f'assets/images/people/{name}.{ext}'
    if not (ROOT/rel).is_file(): errors.append(f'{rel}: missing portrait')


# Canonical typography ownership guardrail.
# Title visual properties belong only in assets/css/typography.css; component layers may keep layout properties.
_typography_owned_selectors=[
    '.eyebrow','.hero h1','.home-hero h1','.page-hero h1',
    '.section-head h2','.content-section h2','.prose h2','.join h2',
    '.challenge h3','.research h3','.research-title','.impact h3','.partner h3','.highlight h3','.news-row h3',
    '.person h3','.team-grid .person h3','.pub h3','.contact-card h3','.join-item h3',
    '.person-detail h2','.detail-block h3','.person-detail .detail-block h3','.research-direction h2',
    '.challenge .num','.highlight .num','.join-item .num'
]
_typography_owned_props={'font-size','font-weight','color','line-height','letter-spacing','text-transform'}
for rel in ('assets/css/site.css','assets/css/refine-base.css','assets/css/app-core.css'):
    css=(ROOT/rel).read_text(encoding='utf-8')
    for match in re.finditer(r'([^{}]+)\{([^{}]*)\}',css):
        selector=match.group(1).strip()
        if not any(token in selector for token in _typography_owned_selectors):
            continue
        props={part.split(':',1)[0].strip().lower() for part in match.group(2).split(';') if ':' in part}
        bad=sorted(props&_typography_owned_props)
        if bad:
            errors.append(f'{rel}: canonical title typography leaked into "{selector}" ({", ".join(bad)}); use typography.css')

_typography=(ROOT/'assets/css/typography.css').read_text(encoding='utf-8')
for required in ('--title-display-size','--title-page-size','--title-section-size','--title-feature-size','--title-item-size','--title-minor-size'):
    if required not in _typography:
        errors.append(f'assets/css/typography.css: missing canonical title contract {required}')

# Semantic title classes are the canonical presentation contract; typography.css must not depend on page structure.
for required in ('.title-display{','.title-page{','.title-section{','.title-feature{','.title-item{','.title-minor{','.item-index{'):
    if required not in _typography:
        errors.append(f'assets/css/typography.css: missing semantic rule {required}')
for banned in ('.home-hero h1','.page-hero h1','.section-head h2','.research h3','.partner h3','.highlight h3','.person-detail .detail-block h3'):
    if banned in _typography:
        errors.append(f'assets/css/typography.css: structural fallback remains ({banned}); use semantic title classes')

# Faculty detail minor headings must declare their semantic level explicitly.
for base in (ROOT/'people',ROOT/'en'/'people'):
    for html in base.glob('*.html'):
        text=html.read_text(encoding='utf-8')
        for attrs,inner in re.findall(r'<section\b([^>]*)class=["\'][^"\']*\bdetail-block\b[^"\']*["\'][^>]*>(.*?)</section>',text,re.I|re.S):
            m=re.search(r'<h3\b([^>]*)>',inner,re.I)
            if m and 'title-minor' not in m.group(1):
                errors.append(f'{html.relative_to(ROOT)}: detail-block h3 must use title-minor')


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

# Full semantic heading coverage guardrail.
# Every h1/h2/h3 inside <main> must explicitly declare its semantic typography level.
_semantic_heading_classes={'title-display','title-page','title-section','title-feature','title-item','title-minor'}
for html in html_files:
    rel=str(html.relative_to(ROOT))
    if rel=='404.html':
        continue
    text=html_text[html.resolve()]
    main_match=re.search(r'<main\b[^>]*>(.*?)</main>',text,re.I|re.S)
    if not main_match:
        continue
    main=main_match.group(1)
    for m in re.finditer(r'<h([1-3])\b([^>]*)>',main,re.I):
        attrs=m.group(2)
        class_match=re.search(r'class=["\']([^"\']*)["\']',attrs,re.I)
        classes=set(class_match.group(1).split()) if class_match else set()
        if not (classes&_semantic_heading_classes):
            line=text[:main_match.start(1)+m.start()].count('\n')+1
            errors.append(f'{rel}:{line}: h{m.group(1)} must declare a semantic title class')

# Validation must fail the build when any contract is violated.


# PAI terminology / completeness guardrails.
_deprecated_pai_terms=[
    '通信–定位–感知融合','通信-定位-感知融合','通信—定位—感知融合',
    'integrated communication, localization and sensing'
]
for html,text in html_text.items():
    rel=str(Path(html).relative_to(ROOT))
    lower=text.lower()
    for term in _deprecated_pai_terms:
        if term.lower() in lower:
            errors.append(f'{rel}: deprecated PAI integration terminology: {term}')
for rel,required in [
    ('index.html','通信–感知–计算–智能融合'),
    ('about.html','通信–感知–计算–智能融合'),
    ('en/index.html','integrated sensing, communication, computing, and intelligence'),
    ('en/about.html','integrated sensing, communication, computing, and intelligence')
]:
    if required not in (ROOT/rel).read_text(encoding='utf-8'):
        errors.append(f'{rel}: missing canonical PAI integration terminology')

# Public pages need a stable social card, app icon metadata and a keyboard skip link.
for rel in paired:
    for candidate in (rel,'en/'+rel):
        p=ROOT/candidate
        if not p.exists(): continue
        text=p.read_text(encoding='utf-8')
        for token,label in [
            ('og:image','Open Graph image'),('apple-touch-icon','Apple touch icon'),
            ('site.webmanifest','web manifest'),('class="skip-link"','skip link'),('id="main-content"','main landmark target')
        ]:
            if token not in text: errors.append(f'{candidate}: missing {label}')
if not (ROOT/'assets/images/social/pai-share-v3.jpg').exists(): errors.append('missing social share image')
for rel in ('assets/icons/favicon.svg','assets/icons/favicon-32.png','assets/icons/apple-touch-icon.png','assets/icons/icon-192.png','assets/icons/icon-512.png','site.webmanifest'):
    if not (ROOT/rel).exists(): errors.append(f'missing brand asset: {rel}')



# Social preview guardrail.
for html,text in html_text.items():
    rel=str(Path(html).relative_to(ROOT))
    if 'pai-share.png' in text:
        errors.append(f'{rel}: legacy social preview image reference remains; use pai-share-v3.jpg')
    if 'property="og:image"' in text and 'pai-share-v3.jpg' not in text:
        errors.append(f'{rel}: og:image must use the compact social preview image')

if errors:
    print('Validation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

print('Validation passed.')
