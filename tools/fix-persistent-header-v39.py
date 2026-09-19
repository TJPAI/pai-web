from pathlib import Path
import re

js_path=Path('assets/js/site.js')
js=js_path.read_text()

pattern=r"  const renderChrome=\(\)=>\{.*?\n  \};\n  renderChrome\(\);"
replacement=r'''  const renderChrome=()=>{
    const path=normalizedPath();
    const lang=path.startsWith('/en/')?'en':'zh';
    const active=sectionForPath(path);
    const items=navItems(lang);
    const languageLabel=lang==='en'?'中文':'EN';
    const languageHref=counterpartWithContext(path);
    const markup=items.map(([label,href])=>{
      const key=sectionForPath(href);
      return `<a${key===active?' class="active" aria-current="page"':''} href="${root(href)}">${label}</a>`;
    }).join('')+`<a href="${root(languageHref)}">${languageLabel}</a>`;

    const header=document.querySelector('.site-header');
    if(header){
      const brand=header.querySelector('.brand');
      if(brand) brand.href=root(lang==='en'?'/en/':'/');
      const nav=header.querySelector('.nav-links');
      let mobile=header.querySelector('.mobile-menu');
      if(!mobile){
        mobile=document.createElement('nav');
        mobile.className='mobile-menu';
        header.appendChild(mobile);
      }

      const needsRebuild=header.dataset.paiLang!==lang||!nav||!nav.querySelector('a')||!mobile.querySelector('a');
      if(needsRebuild){
        if(nav) nav.innerHTML=markup;
        mobile.innerHTML=markup;
        header.dataset.paiLang=lang;
      }else{
        /* Same-language navigation keeps the permanent header DOM intact.
           Only state/hrefs change, avoiding a Safari header repaint on every page swap. */
        const syncLinks=container=>{
          if(!container) return;
          [...container.querySelectorAll('a')].forEach(link=>{
            const label=(link.textContent||'').trim();
            const isLanguage=label==='EN'||label==='中文';
            if(isLanguage){
              link.href=root(languageHref);
              link.classList.remove('active');
              link.removeAttribute('aria-current');
              return;
            }
            let key='';
            try{ key=sectionForPath(normalizedPath(new URL(link.href,location.href).pathname)); }catch(_e){}
            const isActive=!!active&&key===active;
            link.classList.toggle('active',isActive);
            if(isActive) link.setAttribute('aria-current','page');
            else link.removeAttribute('aria-current');
          });
        };
        syncLinks(nav);
        syncLinks(mobile);
      }

      if(nav) nav.setAttribute('aria-label',lang==='en'?'Main navigation':'主导航');
      mobile.id='mobile-navigation';
      mobile.setAttribute('aria-label',lang==='en'?'Mobile navigation':'移动导航');
      mobile.classList.remove('open');
      const button=header.querySelector('.menu-btn');
      if(button){
        button.type='button';
        button.setAttribute('aria-expanded','false');
        button.setAttribute('aria-controls','mobile-navigation');
        button.setAttribute('aria-label',lang==='en'?'Open menu':'打开菜单');
      }
    }

    const footer=document.querySelector('.site-footer');
    if(footer){
      const links=items.map(([label,href])=>`<a href="${root(href)}">${label}</a>`).join('')+
        `<a href="${root(languageHref)}">${languageLabel}</a>`;
      const contact=lang==='en'?
        `4800 Cao'an Highway, Jiading District, Shanghai<br>Tongji University Jiading Campus<br><a href="mailto:23666042@tongji.edu.cn">23666042@tongji.edu.cn</a>`:
        `上海市嘉定区曹安公路4800号<br>同济大学嘉定校区智信馆<br><a href="mailto:23666042@tongji.edu.cn">23666042@tongji.edu.cn</a>`;
      footer.classList.add('compact-footer');
      footer.innerHTML=`<div class="container"><div class="footer-grid"><div><div class="brand"><strong>PAI</strong><span>PAI Research Center · Tongji University</span></div></div><div class="footer-links">${links}</div><div class="footer-contact">${contact}</div></div><div class="footer-meta"><span>© PAI Research Center</span></div></div>`;
    }
  };
  renderChrome();'''

new_js,count=re.subn(pattern,replacement,js,flags=re.S)
if count!=1:
    raise SystemExit(f'renderChrome replacement count={count}')
js_path.write_text(new_js)

css_path=Path('assets/css/site.css')
css=css_path.read_text()
old="  .site-header{background:#fff;backdrop-filter:none;-webkit-backdrop-filter:none;isolation:isolate;z-index:80}"
new="  .site-header{background:#fff;backdrop-filter:none;-webkit-backdrop-filter:none;isolation:isolate;z-index:80;transform:translateZ(0);-webkit-transform:translateZ(0);backface-visibility:hidden;-webkit-backface-visibility:hidden}"
if old not in css:
    raise SystemExit('mobile header rule not found')
css=css.replace(old,new,1)
css_path.write_text(css)

# cache-bust only the files actually changed
for p in Path('.').rglob('*.html'):
    text=p.read_text()
    text=re.sub(r'assets/js/site\.js\?v=20260919-\d+', 'assets/js/site.js?v=20260920-39', text)
    text=re.sub(r'(?:\.\./)*assets/js/site\.js\?v=20260919-\d+', lambda m: re.sub(r'v=20260919-\d+', 'v=20260920-39', m.group(0)), text)
    text=re.sub(r'assets/css/site\.css\?v=20260919-\d+', 'assets/css/site.css?v=20260920-39', text)
    text=re.sub(r'(?:\.\./)*assets/css/site\.css\?v=20260919-\d+', lambda m: re.sub(r'v=20260919-\d+', 'v=20260920-39', m.group(0)), text)
    p.write_text(text)
