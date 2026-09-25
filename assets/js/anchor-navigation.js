(function(){
  'use strict';

  document.addEventListener('click',event=>{
    if(event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
    const link=event.target.closest&&event.target.closest('a[href]');
    if(!link) return;
    const main=document.querySelector('main');
    if(!main?.querySelector('.home-hero')) return;

    let url;
    try{ url=new URL(link.href,location.href); }catch(_e){ return; }
    if(url.origin!==location.origin||url.hash!=='#main-content') return;

    // Page-top homepage CTAs must never briefly inherit the current page scroll
    // while the lightweight router initializes the destination page.
    event.preventDefault();
    event.stopPropagation();
    location.assign(url.href);
  },true);
})();
