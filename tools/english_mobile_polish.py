from pathlib import Path

p=Path('assets/css/app-core.css')
s=p.read_text()
marker='/* English mobile reading polish — 2026-09-19 */'
block=r'''

/* English mobile reading polish — 2026-09-19 */
@media(max-width:768px){
  html[lang="en"] .research-title{font-size:26px!important;line-height:1.17!important;letter-spacing:-.022em!important;max-width:15.5em!important}
  html[lang="en"] .research-detail>p:not(.direction-keywords),
  html[lang="en"] .contact-card>p,
  html[lang="en"] .prose>p{max-width:34em}

  html[lang="en"] .team-grid .person .research-line{margin-bottom:11px}
  html[lang="en"] .team-grid .person .bio-short{color:#747D8B;margin-bottom:11px}
  html[lang="en"] .team-grid .person .person-link,
  html[lang="en"] .team-grid .person>a:last-child{display:inline-block;margin-top:3px}

  html[lang="en"] .prose h2+p{margin-top:16px}

  html[lang="en"] .contact-card .title-item{letter-spacing:-.018em!important}
}
'''
if marker not in s:
    p.write_text(s.rstrip()+block+'\n')

# Publish an English-only cache entry. The shared entry file changes its nested imports,
# while Chinese HTML keeps requesting its already-cached v8 entry and is visually unchanged.
r=Path('assets/css/refine.css')
rs=r.read_text().replace('20260919-8','20260919-9')
r.write_text(rs)
for f in Path('en').rglob('*.html'):
    t=f.read_text()
    t=t.replace('site.css?v=20260919-8','site.css?v=20260919-9')
    t=t.replace('refine.css?v=20260919-8','refine.css?v=20260919-9')
    f.write_text(t)

c=Path('en/contact.html')
t=c.read_text().replace('Tang · Research Assistant','Tang, Research Assistant')
c.write_text(t)
