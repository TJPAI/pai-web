from pathlib import Path
import re, html

ROOT=Path('.')
BASE='https://tjpai.github.io/pai-web'

# 1) Core terminology and related capability wording across user-facing HTML.
repls={
    '通信–定位–感知融合问题':'通信–感知–计算–智能融合',
    '通信-定位-感知融合问题':'通信–感知–计算–智能融合',
    '通信–定位–感知融合':'通信–感知–计算–智能融合',
    '通信-定位-感知融合':'通信–感知–计算–智能融合',
    'integrated communication, localization and sensing':'integrated sensing, communication, computing, and intelligence',
    'communication foundation models':'foundation models for communications',
    'integrated communication-sensing-computing':'integrated sensing, communication & computing',
    'integrated sensing-computing':'integrated sensing, communication & computing',
    '>Research Translation<':'>Research Translation &amp; Applications<',
}
for p in list(ROOT.glob('*.html')) + list((ROOT/'en').rglob('*.html')) + list((ROOT/'people').rglob('*.html')):
    if p.name=='404.html':
        continue
    s=p.read_text()
    for a,b in repls.items(): s=s.replace(a,b)
    p.write_text(s)

# 2) More natural umbrella statements that need more than a mechanical replacement.
p=ROOT/'about.html'; s=p.read_text()
s=s.replace('面向复杂与极限环境，围绕通信–感知–计算–智能融合，构建精准感知、可靠连接与可信协同能力。',
            '面向复杂与极限环境，围绕通信–感知–计算–智能融合，构建精准感知、可靠连接、智能处理与可信协同能力。')
s=s.replace('PAI研究中心围绕复杂场景的通信–感知–计算–智能融合，聚焦三大特色方向：',
            'PAI研究中心围绕复杂环境中的通信–感知–计算–智能融合问题，聚焦三大特色方向：')
s=s.replace('持续提升复杂场景下精准感知、可靠连接与可信协同能力。',
            '持续提升复杂场景下精准感知、可靠连接、智能处理与可信协同能力。')
s=s.replace('<div class="eyebrow">TEAM OVERVIEW</div><h2 class="title-section">团队概况</h2>',
            '<div class="eyebrow">PAI OVERVIEW</div><h2 class="title-section">PAI 概览</h2>')
p.write_text(s)

p=ROOT/'en'/'about.html'; s=p.read_text()
s=s.replace('PAI Research Center addresses integrated sensing, communication, computing, and intelligence in complex and extreme environments.',
            'PAI Research Center advances integrated sensing, communication, computing, and intelligence for complex and extreme environments.')
s=s.replace('Our work is organized around three directions:',
            'Our work focuses on integrated sensing, communication, computing, and intelligence across three research directions:')
s=s.replace('<div class="eyebrow">TEAM OVERVIEW</div><h2 class="title-section">At a Glance</h2>',
            '<div class="eyebrow">PAI OVERVIEW</div><h2 class="title-section">At a Glance</h2>')
p.write_text(s)

# Homepage meta wording, preserving brand hero copy.
p=ROOT/'index.html'; s=p.read_text()
s=s.replace('围绕通信–感知–计算–智能融合，聚焦高精定位与智能感知、鲁棒通信与可靠组网、智能处理与可信协同。',
            '围绕通信–感知–计算–智能融合，聚焦高精定位与智能感知、鲁棒通信与可靠组网、智能处理与可信协同。')
p.write_text(s)
p=ROOT/'en'/'index.html'; s=p.read_text()
s=s.replace('PAI Research Center at Tongji University advances integrated sensing, communication, computing, and intelligence for complex and extreme environments.',
            'PAI Research Center at Tongji University advances integrated sensing, communication, computing, and intelligence for complex and extreme environments.')
p.write_text(s)

# 3) Align the selected homepage achievements in Chinese and English.
cn=ROOT/'index.html'; s=cn.read_text()
start=s.index('<div class="highlights">', s.index('Research Excellence'))
end=s.index('</div><a class="text-link" href="about.html#achievements">', start)
cn_block='''<div class="highlights"><article class="highlight"><div class="num item-index">01</div><div><h3 class="title-item">微软全球室内定位技术大赛冠军</h3><p>2016 年冠军，2018 年获得亚军。</p></div></article><article class="highlight"><div class="num item-index">02</div><div><h3 class="title-item">中国国际工业博览会重要奖项</h3><p>2014 年磁通信技术获中国国际工业博览会特等奖；2016 年室内定位技术获工博会创新银奖。</p></div></article><article class="highlight"><div class="num item-index">03</div><div><h3 class="title-item">中国“互联网+”大学生创新创业大赛全国金奖</h3></div></article><article class="highlight"><div class="num item-index">04</div><div><h3 class="title-item">省部级重要科技奖励</h3><p>教育部技术发明一等奖、上海市技术发明一等奖、上海市科技进步一等奖。</p></div></article><article class="highlight"><div class="num item-index">05</div><div><h3 class="title-item">中国国际进口博览会智能导览系统</h3><p>高精定位与智能导航技术应用于国家会展中心大型复杂场馆。</p></div></article>'''
s=s[:start]+cn_block+s[end:]; cn.write_text(s)

en=ROOT/'en'/'index.html'; s=en.read_text()
start=s.index('<div class="highlights">', s.index('Research Excellence'))
end=s.index('</div><a class="text-link" href="about.html#achievements">', start)
en_block='''<div class="highlights"><article class="highlight"><div class="num item-index">01</div><div><h3 class="title-item">Champion, Microsoft Indoor Localization Competition</h3><p>Champion in 2016 and runner-up in 2018.</p></div></article><article class="highlight"><div class="num item-index">02</div><div><h3 class="title-item">China International Industry Fair Awards</h3><p>Top Award for magnetic communication in 2014 and Innovation Silver Award for indoor localization in 2016.</p></div></article><article class="highlight"><div class="num item-index">03</div><div><h3 class="title-item">National Gold Award, China “Internet+” Innovation and Entrepreneurship Competition</h3></div></article><article class="highlight"><div class="num item-index">04</div><div><h3 class="title-item">Major Science and Technology Awards</h3><p>Major first-prize awards from the Ministry of Education and Shanghai Municipality.</p></div></article><article class="highlight"><div class="num item-index">05</div><div><h3 class="title-item">Smart Navigation System for the China International Import Expo</h3><p>High-precision localization and intelligent navigation deployed at the National Exhibition and Convention Center.</p></div></article>'''
s=s[:start]+en_block+s[end:]; en.write_text(s)

# 4) Standardize English footer address everywhere, including faculty detail pages.
footer='''<div class="footer-contact">Zhixin Building, Tongji University Jiading Campus<br>4800 Cao'an Highway, Jiading District, Shanghai<br><a href="mailto:23666042@tongji.edu.cn">23666042@tongji.edu.cn</a></div>'''
for p in (ROOT/'en').rglob('*.html'):
    s=p.read_text()
    s=re.sub(r'<div class="footer-contact">.*?</div>', footer, s, count=1, flags=re.S)
    p.write_text(s)

# 5) Remove obsolete CSS compatibility-shim links from all HTML.
for p in list(ROOT.glob('*.html')) + list((ROOT/'en').rglob('*.html')) + list((ROOT/'people').rglob('*.html')):
    s=p.read_text()
    s=re.sub(r'<link rel="stylesheet" href="(?:\.\./)*assets/css/(?:app|team)\.css">','',s)
    p.write_text(s)

# 6) SEO: canonical, language alternates, x-default and basic Open Graph.
def urls_for(path):
    posix=path.as_posix()
    is_en=posix.startswith('en/')
    rel=posix[3:] if is_en else posix
    if rel=='index.html':
        zh=BASE+'/'
        enu=BASE+'/en/'
    elif rel.startswith('people/'):
        zh=BASE+'/'+rel
        enu=BASE+'/en/'+rel
    else:
        zh=BASE+'/'+rel
        enu=BASE+'/en/'+rel
    return (enu if is_en else zh), zh, enu

paired={'index.html','about.html','team.html','research.html','publications.html','join.html','contact.html'}
for p in list(ROOT.glob('*.html')) + list((ROOT/'people').glob('*.html')) + list((ROOT/'en').glob('*.html')) + list((ROOT/'en'/'people').glob('*.html')):
    if p.name=='404.html': continue
    s=p.read_text()
    if 'rel="canonical"' in s: continue
    mt=re.search(r'<title>(.*?)</title>',s,re.S)
    md=re.search(r'<meta name="description" content="([^"]*)">',s)
    if not mt or not md: continue
    title=mt.group(1); desc=md.group(1)
    canonical, zh, enu=urls_for(p)
    rel=p.as_posix()[3:] if p.as_posix().startswith('en/') else p.as_posix()
    has_pair=(rel in paired or rel.startswith('people/')) and (ROOT/'en'/rel).exists() and (ROOT/rel).exists()
    tags=[f'<link rel="canonical" href="{canonical}">']
    if has_pair:
        tags += [f'<link rel="alternate" hreflang="zh-CN" href="{zh}">',f'<link rel="alternate" hreflang="en" href="{enu}">',f'<link rel="alternate" hreflang="x-default" href="{zh}">']
    tags += ['<meta property="og:type" content="website">',f'<meta property="og:title" content="{title}">',f'<meta property="og:description" content="{desc}">',f'<meta property="og:url" content="{canonical}">']
    marker=md.group(0)
    s=s.replace(marker, marker+''.join(tags),1)
    p.write_text(s)

# 7) One shared cache version for both languages and nested CSS.
for p in list(ROOT.glob('*.html')) + list((ROOT/'people').rglob('*.html')) + list((ROOT/'en').rglob('*.html')):
    if p.name=='404.html': continue
    s=p.read_text()
    s=re.sub(r'site\.css\?v=20260919-\d+', 'site.css?v=20260919-10', s)
    s=re.sub(r'refine\.css\?v=20260919-\d+', 'refine.css?v=20260919-10', s)
    p.write_text(s)
r=ROOT/'assets/css/refine.css'; s=r.read_text(); s=re.sub(r'20260919-\d+', '20260919-10', s); r.write_text(s)

# 8) Guardrails for this migration.
all_html='\n'.join(p.read_text() for p in list(ROOT.glob('*.html')) + list((ROOT/'en').rglob('*.html')) + list((ROOT/'people').rglob('*.html')))
for old in ['通信–定位–感知融合','通信-定位-感知融合','integrated communication, localization and sensing','communication foundation models','integrated communication-sensing-computing','integrated sensing-computing']:
    if old in all_html: raise SystemExit('legacy wording remains: '+old)
if '通信–感知–计算–智能融合' not in all_html: raise SystemExit('new Chinese umbrella wording missing')
if 'integrated sensing, communication, computing, and intelligence' not in all_html: raise SystemExit('new English umbrella wording missing')
