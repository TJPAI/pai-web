from pathlib import Path

zh = Path('publications.html')
en = Path('en/publications.html')
css = Path('assets/css/refine.css')

z = zh.read_text(encoding='utf-8')
e = en.read_text(encoding='utf-8')
c = css.read_text(encoding='utf-8')

old_zh = '<a class="results-news-row" href="https://doi.org/10.1109/TVT.2026.3721188" target="_blank" rel="noopener noreferrer"><time datetime="2026">2026</time><span>透地磁感应通信研究发表于 IEEE Transactions on Vehicular Technology</span></a><div class="results-news-row"><time datetime="2025-06">2025.06</time><span>IEEE Global Blockchain Conference 2025 在上海举办</span></div>'
new_zh = '<a class="results-news-row" href="https://doi.org/10.1109/TWC.2026.3667951" target="_blank" rel="noopener noreferrer"><time datetime="2026">2026</time><span>Hexin Feng 等去中心化联邦学习研究发表于 IEEE TWC</span></a><a class="results-news-row" href="https://doi.org/10.1109/TWC.2026.3659648" target="_blank" rel="noopener noreferrer"><time datetime="2026">2026</time><span>Hanfu Zhang 等 IRS 辅助通感一体研究发表于 IEEE TWC</span></a>'
old_en = '<a class="results-news-row" href="https://doi.org/10.1109/TVT.2026.3721188" target="_blank" rel="noopener noreferrer"><time datetime="2026">2026</time><span>Through-the-Earth magnetic induction study published in IEEE Transactions on Vehicular Technology</span></a><div class="results-news-row"><time datetime="2025-06">2025.06</time><span>IEEE Global Blockchain Conference 2025 held in Shanghai</span></div>'
new_en = '<a class="results-news-row" href="https://doi.org/10.1109/TWC.2026.3667951" target="_blank" rel="noopener noreferrer"><time datetime="2026">2026</time><span>Hexin Feng et al. publish decentralized federated learning study in IEEE TWC</span></a><a class="results-news-row" href="https://doi.org/10.1109/TWC.2026.3659648" target="_blank" rel="noopener noreferrer"><time datetime="2026">2026</time><span>Hanfu Zhang et al. publish IRS-assisted ISAC study in IEEE TWC</span></a>'

if z.count(old_zh) != 1 or e.count(old_en) != 1:
    raise SystemExit('news anchors not found exactly once')
z = z.replace(old_zh, new_zh, 1)
e = e.replace(old_en, new_en, 1)

old_css = '''@media(max-width:768px){
  .page-results .page-hero>.container.std{grid-template-columns:minmax(0,.84fr) minmax(0,1.16fr);column-gap:18px}
  .page-results .page-hero>.container.std>.title-page{font-size:clamp(38px,10.5vw,52px)}
  .page-results .page-hero>.container.std>p{font-size:clamp(13px,3.7vw,17px);line-height:1.55}
  .results-news{padding-left:16px}
  .results-news h2{margin-bottom:8px;font-size:15px}
  .results-news-row{grid-template-columns:52px minmax(0,1fr);gap:8px;padding:7px 0}
  .results-news-row time{font-size:10px;line-height:1.45}
  .results-news-row span{font-size:11px;line-height:1.45;font-weight:570}
}
@media(max-width:380px){
  .page-results .page-hero>.container.std{grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);column-gap:14px}
  .results-news{padding-left:12px}
  .results-news-row{grid-template-columns:46px minmax(0,1fr);gap:6px}
  .results-news-row span{font-size:10.5px}
}'''
new_css = '''@media(max-width:768px){
  .page-results .page-hero>.container.std{grid-template-columns:minmax(0,.48fr) minmax(0,.52fr);column-gap:14px}
  .page-results .page-hero>.container.std>.title-page{font-size:clamp(38px,10.5vw,52px)}
  .page-results .page-hero>.container.std>p{font-size:clamp(13px,3.55vw,16px);line-height:1.52}
  .results-news{padding-left:12px}
  .results-news h2{margin-bottom:6px;font-size:14px;font-weight:620}
  .results-news-row{grid-template-columns:40px minmax(0,1fr);gap:6px;padding:6px 0}
  .results-news-row time{font-size:9.5px;line-height:1.4}
  .results-news-row span{font-size:10.5px;line-height:1.42;font-weight:540}
}
@media(max-width:380px){
  .page-results .page-hero>.container.std{grid-template-columns:minmax(0,.49fr) minmax(0,.51fr);column-gap:12px}
  .results-news{padding-left:10px}
  .results-news-row{grid-template-columns:36px minmax(0,1fr);gap:5px}
  .results-news-row span{font-size:10px}
}'''
if c.count(old_css) != 1:
    raise SystemExit('mobile css anchor not found exactly once')
c = c.replace(old_css, new_css, 1)

zh.write_text(z, encoding='utf-8')
en.write_text(e, encoding='utf-8')
css.write_text(c, encoding='utf-8')
