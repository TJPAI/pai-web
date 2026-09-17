#!/usr/bin/env python3
from pathlib import Path
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

# Check common local href/src references in HTML.
for html in ROOT.rglob('*.html'):
    text=html.read_text(encoding='utf-8')
    for attr,target in re.findall(r'\b(href|src)=["\']([^"\']+)["\']',text):
        if target.startswith(('http://','https://','mailto:','tel:','#','data:','javascript:')):
            continue
        target=target.split('#',1)[0].split('?',1)[0]
        if not target: continue
        resolved=(html.parent/target).resolve()
        try: resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f'{html.relative_to(ROOT)}: path escapes site: {target}')
            continue
        if not resolved.exists():
            errors.append(f'{html.relative_to(ROOT)}: missing local {attr}: {target}')

if errors:
    print('\n'.join('ERROR: '+e for e in errors))
    sys.exit(1)
print('Validation passed.')
