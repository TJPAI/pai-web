#!/usr/bin/env python3
from pathlib import Path

p=Path('tools/validate.py')
text=p.read_text(encoding='utf-8')
marker='# Full semantic heading coverage guardrail.'
if marker in text:
    raise SystemExit('guard already present')
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
p.write_text(text.rstrip()+append,encoding='utf-8')
