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
            ('assets/js/site.js','shared runtime')
        ]:
            if token not in text:
                errors.append(f'{rel}: missing {name}')

        ids=re.findall(r'\bid=["\']([^"\']+)["\']',text)
        duplicates=sorted({value for value in ids if ids.count(value)>1})
        if duplicates:
            errors.append(f'{rel}: duplicate id(s): {", ".join(duplicates)}')

        main_match=re.search(r'<main\b[^>]*>(.*?)</main>',text,re.I|re.S)
        if main_match and re.search(r'<style\b',main_match.group(1),re.I):
            errors.append(f'{rel}: page-local <style> inside <main>; move shared presentation to CSS')

    if '高水平科研与代表成果' in text:
        errors.append(f'{rel}: deprecated heading "高水平科研与代表成果"; use "代表性成果"')

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

# Chinese/English page pairs should stay complete.
paired=[
    'index.html','about.html','research.html','team.html','publications.html','join.html','contact.html',
    'people/erwu-liu.html','people/rui-wang.html','people/gang-shen.html','people/dunhui-xiao.html','people/shuyan-hu.html','people/yan-liu.html'
]
for rel in paired:
    en_rel='en/'+rel
    if not (ROOT/rel).exists(): errors.append(f'missing Chinese page: {rel}')
    if not (ROOT/en_rel).exists(): errors.append(f'missing English page: {en_rel}')

# Architectural guardrails: one shared behavior runtime, static presentation, no direct Cache API routing.
site_js=(ROOT/'assets/js/site.js').read_text(encoding='utf-8')
for banned,reason in [
    ('stopImmediatePropagation','event handlers should not suppress unrelated handlers'),
    ('caches.keys(','page runtime must not select Service Worker caches directly'),
    ('installSharedStyles','runtime CSS injection is not allowed')
]:
    if banned in site_js:
        errors.append(f'assets/js/site.js: {reason} ({banned})')

app_css=ROOT/'assets/css/app.css'
if not app_css.exists():
    errors.append('assets/css/app.css: missing shared interactive presentation layer')

sw=(ROOT/'sw.js').read_text(encoding='utf-8')
if 'skipWaiting(' in sw:
    errors.append('sw.js: skipWaiting must not be used; it can mix old JS with a new cached bundle')
if './assets/css/app.css' not in sw:
    errors.append('sw.js: app.css must be precached')

if errors:
    print('\n'.join('ERROR: '+e for e in errors))
    sys.exit(1)
print('Validation passed.')
