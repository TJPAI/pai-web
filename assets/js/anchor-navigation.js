(function(){
  'use strict';

  const header=document.querySelector('.site-header');
  if(header&&!header.id) header.id='page-top';

  document.addEventListener('click',event=>{
    if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    const link=event.target.closest&&event.target.closest('a[href]');
    if(!link) return;
    const main=document.querySelector('main');
    if(!main?.querySelector('.home-hero')) return;

    let url;
    try{ url=new URL(link.href,location.href); }catch(_e){ return; }
    if(url.origin!==location.origin||url.hash!=='#main-content') return;

    // Keep these CTAs inside the site's lightweight router so the current
    // page's scroll position is written into history and restored by Back.
    // Point at the persistent header instead of main-content so the target
    // page lands at the same visual top as choosing it from the main menu.
    url.hash='#page-top';
    link.href=url.href;
  },true);
})();
