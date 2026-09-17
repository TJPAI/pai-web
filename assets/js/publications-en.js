(function(){
  const root=document.querySelector('[data-publications]');
  if(!root) return;
  const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const doiHref=doi=>'https://doi.org/'+String(doi).trim().split('/').map(encodeURIComponent).join('/');
  Promise.all([
    fetch('../data/publications.json').then(r=>{if(!r.ok) throw new Error('Failed to load recent publications'); return r.json();}),
    fetch('../data/publications-archive.json').then(r=>r.ok?r.json():[])
  ]).then(parts=>parts.flat()).then(items=>{
    const byYear=new Map();
    items.sort((a,b)=>b.year-a.year).forEach(item=>{
      if(!byYear.has(item.year)) byYear.set(item.year,[]);
      byYear.get(item.year).push(item);
    });
    root.innerHTML='';
    for(const [year,pubs] of byYear){
      const section=document.createElement('section');
      section.className='pub-group';
      section.innerHTML=`<div class="pub-year-row"><h2 class="pub-year">${year}</h2><span>${pubs.length} publication${pubs.length===1?'':'s'}</span></div>`;
      pubs.forEach(p=>{
        const article=document.createElement('article');
        article.className='pub';
        const actions=p.doi?`<div class="pub-actions"><a href="${esc(doiHref(p.doi))}" target="_blank" rel="noopener">DOI ↗</a></div>`:'';
        article.innerHTML=`<h3>${esc(p.title)}</h3><p class="pub-authors">${esc(p.authors)}</p><p class="pub-venue">${esc(p.venue)} · ${year}</p>${actions}`;
        section.appendChild(article);
      });
      root.appendChild(section);
    }
  }).catch(()=>{root.innerHTML='<p class="muted">Publications are temporarily unavailable. Please refresh later.</p>';});
})();
