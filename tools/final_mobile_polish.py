from pathlib import Path

p = Path('assets/css/app-core.css')
s = p.read_text()
marker = '/* Final mobile micro-polish — 2026-09-19 */'
block = r'''

/* Final mobile micro-polish — 2026-09-19 */
@media(max-width:768px){
  /* Contact: trim only the remaining excess vertical air. */
  .contact-grid{gap:18px;margin-top:-10px}
  .contact-card{padding:20px 0}

  /* Research: one more small reduction between directions, without touching type scale. */
  .research-direction{padding-top:48px!important;padding-bottom:49px!important}

  /* About international impact: editorial list, quieter descriptions and clearer grouping. */
  #international-impact .detail-block{padding-bottom:30px}
  #international-impact .detail-block+.detail-block{margin-top:4px}
  #international-impact .detail-block h3{margin-bottom:5px}
  #international-impact .detail-block p{color:#7B8492}

  /* Publications: preserve title prominence and separate metadata layers. */
  .pub{border-top-color:#EEF0F3}
  .pub-authors{color:#78808D!important}
  .pub-venue{margin-top:5px!important;color:#9299A5!important}
  .pub-actions{margin-top:13px;color:#747C89}

  /* Footer: keep size, reduce visual weight. */
  .compact-footer .brand span{opacity:.48}
  .compact-footer .footer-contact{color:rgba(255,255,255,.40)}
  .compact-footer .footer-meta{margin-top:10px;padding-top:8px;color:rgba(255,255,255,.34)}
}
'''
if marker not in s:
    p.write_text(s.rstrip() + block + '\n')

# Bump shared cache chain from v7 to v8 so Safari cannot mix old and new polish.
r = Path('assets/css/refine.css')
rs = r.read_text().replace('20260919-7', '20260919-8')
r.write_text(rs)
for f in Path('.').rglob('*.html'):
    t = f.read_text()
    t2 = t.replace('site.css?v=20260919-7', 'site.css?v=20260919-8')
    t2 = t2.replace('refine.css?v=20260919-7', 'refine.css?v=20260919-8')
    if t2 != t:
        f.write_text(t2)
