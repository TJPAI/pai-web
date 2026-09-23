from pathlib import Path
import re

zh_path = Path('index.html')
en_path = Path('en/index.html')
css_path = Path('assets/css/refine.css')
zh = zh_path.read_text()
en = en_path.read_text()
css = css_path.read_text()

zh_visuals = '''<div class="impact-visuals" aria-label="代表性应用场景"><figure class="impact-visual"><a href="https://alumni.tongji.edu.cn/e4/74/c28134a255092/page.htm" target="_blank" rel="noopener noreferrer"><img src="https://alumni.tongji.edu.cn/_upload/article/images/fb/51/b84db8744a1bbde5e391c9c4f2ca/704165f6-fb67-4d2a-b952-f61cb2a2ea5a.png" alt="进博会大型场馆定位导航与智能导览应用" loading="lazy" decoding="async"><figcaption><strong>进博会 · 高精定位与智能导览</strong>高精定位、室内导航与 AR 场景服务应用于国家会展中心。<span class="impact-visual-source">同济大学官方报道</span></figcaption></a></figure><figure class="impact-visual impact-visual-mine"><a href="https://news.tongji.edu.cn/info/1006/29027.htm" target="_blank" rel="noopener noreferrer"><img src="https://news.tongji.edu.cn/_mediafile/tjnews/photos/images/2014/4/25/650/bdj4sjswou5jxkd.jpg" alt="深穿透磁通信救援设备工程应用" loading="lazy" decoding="async"><figcaption><strong>煤矿 · 跨介质磁通信</strong>面向地下复杂介质环境开展透地磁通信与可靠连接验证。<span class="impact-visual-source">同济大学新闻网 / 新华社</span></figcaption></a></figure></div>'''
en_visuals = '''<div class="impact-visuals" aria-label="Representative application scenarios"><figure class="impact-visual"><a href="https://alumni.tongji.edu.cn/e4/74/c28134a255092/page.htm" target="_blank" rel="noopener noreferrer"><img src="https://alumni.tongji.edu.cn/_upload/article/images/fb/51/b84db8744a1bbde5e391c9c4f2ca/704165f6-fb67-4d2a-b952-f61cb2a2ea5a.png" alt="Indoor localization and smart navigation at the China International Import Expo" loading="lazy" decoding="async"><figcaption><strong>CIIE · High-Precision Localization &amp; Smart Navigation</strong>Indoor localization, routing and AR guidance deployed at the National Exhibition and Convention Center.<span class="impact-visual-source">Tongji University</span></figcaption></a></figure><figure class="impact-visual impact-visual-mine"><a href="https://news.tongji.edu.cn/info/1006/29027.htm" target="_blank" rel="noopener noreferrer"><img src="https://news.tongji.edu.cn/_mediafile/tjnews/photos/images/2014/4/25/650/bdj4sjswou5jxkd.jpg" alt="Through-the-earth magnetic communication rescue equipment" loading="lazy" decoding="async"><figcaption><strong>Mining · Through-the-Earth Magnetic Communication</strong>Field-proven reliable links through challenging underground media.<span class="impact-visual-source">Tongji University / Xinhua</span></figcaption></a></figure></div>'''

zh, n1 = re.subn(r'<div class="impact-visuals".*?</div>(?=<div class="impact-grid">)', zh_visuals, zh, count=1, flags=re.S)
en, n2 = re.subn(r'<div class="impact-visuals".*?</div>(?=<div class="impact-grid">)', en_visuals, en, count=1, flags=re.S)
if n1 != 1 or n2 != 1:
    raise SystemExit(f'impact replacement failed: zh={n1}, en={n2}')

zh_ach = '''<figure class="home-feature-visual achievement-feature"><a href="https://see.tongji.edu.cn/info/1143/3357.htm" target="_blank" rel="noopener noreferrer"><img src="https://see.tongji.edu.cn/__local/9/93/3D/0B427C67959BBF2EB570EC25939_B112E241_781C3.png?e=.png" alt="PAI团队参加微软全球室内定位技术大赛" loading="lazy" decoding="async"><figcaption><strong>微软全球室内定位技术大赛</strong><span>2016 年冠军 · 奥地利维也纳</span></figcaption></a></figure>'''
en_ach = '''<figure class="home-feature-visual achievement-feature"><a href="https://see.tongji.edu.cn/info/1143/3357.htm" target="_blank" rel="noopener noreferrer"><img src="https://see.tongji.edu.cn/__local/9/93/3D/0B427C67959BBF2EB570EC25939_B112E241_781C3.png?e=.png" alt="PAI team at the Microsoft Indoor Localization Competition" loading="lazy" decoding="async"><figcaption><strong>Microsoft Indoor Localization Competition</strong><span>Champion, 2016 · Vienna, Austria</span></figcaption></a></figure>'''
zh_anchor = '</div><a class="text-link" href="about.html#achievements">查看更多代表成果与平台影响 →</a>'
en_anchor = '</div><a class="text-link" href="about.html#achievements">More achievements and institutional impact →</a>'
if zh_anchor not in zh or en_anchor not in en:
    raise SystemExit('achievement anchor missing')
zh = zh.replace(zh_anchor, '</div>' + zh_ach + '<a class="text-link" href="about.html#achievements">查看更多代表成果与平台影响 →</a>', 1)
en = en.replace(en_anchor, '</div>' + en_ach + '<a class="text-link" href="about.html#achievements">More achievements and institutional impact →</a>', 1)

zh_update = '''<figure class="home-feature-visual update-feature"><a href="https://news.tongji.edu.cn/info/1003/87921.htm" target="_blank" rel="noopener noreferrer"><img src="https://news.tongji.edu.cn/__local/5/09/7C/9DF69DAA2AE2F9F656D71BAD4C7_46EED02F_A6634.png" alt="IEEE主席Thomas Coughlin访问同济大学" loading="lazy" decoding="async"><figcaption><strong>IEEE 主席 Thomas Coughlin 来访</strong><span>国际学术组织交流与合作</span></figcaption></a></figure>'''
en_update = '''<figure class="home-feature-visual update-feature"><a href="https://news.tongji.edu.cn/info/1003/87921.htm" target="_blank" rel="noopener noreferrer"><img src="https://news.tongji.edu.cn/__local/5/09/7C/9DF69DAA2AE2F9F656D71BAD4C7_46EED02F_A6634.png" alt="IEEE President Thomas Coughlin visiting Tongji University" loading="lazy" decoding="async"><figcaption><strong>Visit by IEEE President Thomas Coughlin</strong><span>International academic engagement and collaboration</span></figcaption></a></figure>'''
marker = '<div class="updates-grid">'
if marker not in zh or marker not in en:
    raise SystemExit('updates marker missing')
zh = zh.replace(marker, zh_update + marker, 1)
en = en.replace(marker, en_update + marker, 1)

extra_css = '''\n\n/* Homepage visual storytelling: keep imagery sparse and editorial. */\n.home-feature-visual{margin:30px 0 22px;border:1px solid var(--line);background:var(--soft);overflow:hidden}\n.home-feature-visual a{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(250px,.65fr);align-items:stretch}\n.home-feature-visual img{width:100%;height:100%;min-height:210px;max-height:300px;object-fit:cover}\n.home-feature-visual figcaption{display:flex;flex-direction:column;justify-content:flex-end;padding:24px;color:var(--muted);font-size:13px;line-height:1.55;border-left:1px solid var(--line)}\n.home-feature-visual figcaption strong{color:var(--ink);font-size:16px;font-weight:620;line-height:1.4;margin-bottom:7px}\n.home-feature-visual figcaption span{display:block}\n.achievement-feature{max-width:920px;margin-top:34px}\n.update-feature{margin-top:-10px;margin-bottom:36px}\n.update-feature img{max-height:320px;object-position:center 46%}\n.impact-visual-mine img{object-position:center 45%}\n@media(max-width:768px){\n  .home-feature-visual{margin:24px 0 20px}\n  .home-feature-visual a{grid-template-columns:1fr}\n  .home-feature-visual img{height:auto;min-height:0;max-height:none;aspect-ratio:16/9;object-fit:cover}\n  .home-feature-visual figcaption{padding:14px 16px 16px;border-left:0;border-top:1px solid var(--line)}\n  .home-feature-visual figcaption strong{font-size:14px;margin-bottom:4px}\n  .update-feature{margin-top:0;margin-bottom:28px}\n}\n'''
if '/* Homepage visual storytelling:' not in css:
    css += extra_css

zh = zh.replace('refine.css?v=20260923-01', 'refine.css?v=20260923-02')
en = en.replace('refine.css?v=20260923-01', 'refine.css?v=20260923-02')

zh_path.write_text(zh)
en_path.write_text(en)
css_path.write_text(css)
