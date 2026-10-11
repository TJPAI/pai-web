from pathlib import Path

zh = Path('publications.html')
en = Path('en/publications.html')
css = Path('assets/css/refine.css')

z = zh.read_text(encoding='utf-8')
e = en.read_text(encoding='utf-8')
c = css.read_text(encoding='utf-8')

old_zh = 'Ming Jiang 等 DePIN 综述发表于 IEEE Communications Surveys &amp; Tutorials'
new_zh = 'Ming Jiang 等 DePIN 综述发表于 IEEE COMST'
old_en = 'Ming Jiang et al. publish a DePIN survey in IEEE Communications Surveys &amp; Tutorials'
new_en = 'Ming Jiang et al. publish DePIN survey in IEEE COMST'
if z.count(old_zh) != 1:
    raise SystemExit(f'zh first-news count={z.count(old_zh)}')
if e.count(old_en) != 1:
    raise SystemExit(f'en first-news count={e.count(old_en)}')
z = z.replace(old_zh, new_zh, 1)
e = e.replace(old_en, new_en, 1)

old_css = '''.results-news h2{margin:0 0 12px;font-size:18px;line-height:1.25;font-weight:620;letter-spacing:-.01em}
.results-news-list{border-top:0}
.results-news-row{
  display:grid;
  grid-template-columns:92px minmax(0,1fr);
  gap:18px;
  align-items:start;
  padding:11px 0;
  border-bottom:1px solid var(--line);
  color:inherit;
  text-decoration:none;
}
.results-news-row:last-child{border-bottom:0}
.results-news-row time{color:#8B94A2;font-size:13px;line-height:1.55;font-variant-numeric:tabular-nums}
.results-news-row span{color:var(--ink);font-size:14px;line-height:1.55;font-weight:540}
@media(hover:hover) and (pointer:fine){a.results-news-row:hover span{text-decoration:underline;text-underline-offset:3px}}
@media(max-width:768px){
  .page-results .page-hero>.container.std>.title-page{font-size:clamp(38px,10.5vw,52px)}
  .page-results .page-hero>.container.std>p{font-size:clamp(13px,3.7vw,17px);line-height:1.55}
  .results-news{margin-top:28px;padding-top:20px}
  .results-news h2{margin-bottom:8px;font-size:15px;font-weight:620}
  .results-news-row{grid-template-columns:52px minmax(0,1fr);gap:9px;padding:8px 0}
  .results-news-row time{font-size:10px;line-height:1.45}
  .results-news-row span{font-size:11.5px;line-height:1.48;font-weight:540}
}
@media(max-width:380px){
  .results-news{margin-top:24px;padding-top:18px}
  .results-news-row{grid-template-columns:48px minmax(0,1fr);gap:8px}
  .results-news-row span{font-size:11px}
}'''
new_css = '''.results-news h2{margin:0 0 8px;font-size:18px;line-height:1.25;font-weight:560;letter-spacing:-.01em;color:#4F5968}
.results-news-list{border-top:0}
.results-news-row{
  display:grid;
  grid-template-columns:76px minmax(0,1fr);
  gap:12px;
  align-items:start;
  padding:11px 0;
  border-bottom:1px solid var(--line);
  color:inherit;
  text-decoration:none;
}
.results-news-row:last-child{border-bottom:0}
.results-news-row time{color:#8B94A2;font-size:13px;line-height:1.55;font-variant-numeric:tabular-nums}
.results-news-row span{color:#303744;font-size:14px;line-height:1.55;font-weight:520}
@media(hover:hover) and (pointer:fine){a.results-news-row:hover span{text-decoration:underline;text-underline-offset:3px}}
@media(max-width:768px){
  .page-results .page-hero>.container.std>.title-page{font-size:clamp(38px,10.5vw,52px)}
  .page-results .page-hero>.container.std>p{font-size:clamp(13px,3.7vw,17px);line-height:1.55}
  .results-news{margin-top:28px;padding-top:20px}
  .results-news h2{margin-bottom:4px;font-size:15px;font-weight:560;color:#4F5968}
  .results-news-row{grid-template-columns:44px minmax(0,1fr);gap:7px;padding:8px 0}
  .results-news-row time{font-size:10px;line-height:1.45}
  .results-news-row span{font-size:11.5px;line-height:1.48;font-weight:520;color:#303744}
}
@media(max-width:380px){
  .results-news{margin-top:24px;padding-top:18px}
  .results-news-row{grid-template-columns:42px minmax(0,1fr);gap:6px}
  .results-news-row span{font-size:11px}
}'''
if c.count(old_css) != 1:
    raise SystemExit(f'css block count={c.count(old_css)}')
c = c.replace(old_css, new_css, 1)

zh.write_text(z, encoding='utf-8')
en.write_text(e, encoding='utf-8')
css.write_text(c, encoding='utf-8')
