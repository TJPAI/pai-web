#!/usr/bin/env python3
from pathlib import Path
import re

SEMANTIC={'title-display','title-page','title-section','title-feature','title-item','title-minor'}

def add_class_to_h3_tag(tag, cls):
    m=re.search(r'class=["\']([^"\']*)["\']',tag,re.I)
    if m:
        classes=m.group(1).split()
        if any(c in SEMANTIC for c in classes):
            return tag
        classes.append(cls)
        return tag[:m.start(1)]+' '.join(classes)+tag[m.end(1):]
    return tag[:-1]+f' class="{cls}">'

def add_to_all_h3(path, cls='title-item'):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    text=re.sub(r'<h3\b[^>]*>',lambda m:add_class_to_h3_tag(m.group(0),cls),text,flags=re.I)
    p.write_text(text,encoding='utf-8')

def add_in_articles(path, article_class, cls):
    p=Path(path)
    text=p.read_text(encoding='utf-8')
    pattern=rf'(<article\b[^>]*class=["\'][^"\']*\b{re.escape(article_class)}\b[^"\']*["\'][^>]*>)(.*?)(</article>)'
    def repl(m):
        body=re.sub(r'<h3\b[^>]*>',lambda x:add_class_to_h3_tag(x.group(0),cls),m.group(2),count=1,flags=re.I)
        return m.group(1)+body+m.group(3)
    text=re.sub(pattern,repl,text,flags=re.I|re.S)
    p.write_text(text,encoding='utf-8')

# Explicit semantic levels for the remaining static headings.
for path in ('about.html','join.html','contact.html','en/about.html','en/join.html','en/contact.html'):
    add_to_all_h3(path,'title-item')
for path in ('index.html','en/index.html'):
    add_in_articles(path,'challenge','title-item')
    add_in_articles(path,'highlight','title-item')
    add_in_articles(path,'impact','title-feature')

# Strengthen validation and restore its final failure exit.
p=Path('tools/validate.py')
text=p.read_text(encoding='utf-8')
text=text.replace("('--title-display-size','--title-page-size','--title-section-size','--title-feature-size','--title-item-size','--title-minor-size','.research-title')","('--title-display-size','--title-page-size','--title-section-size','--title-feature-size','--title-item-size','--title-minor-size')")
marker='# Full semantic heading coverage guardrail.'
if marker not in text:
    append=r'''

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
if errors:
    print('Validation failed:')
    for error in errors:
        print(f' - {error}')
    sys.exit(1)

print('Validation passed.')
'''
    text=text.rstrip()+append
p.write_text(text,encoding='utf-8')
