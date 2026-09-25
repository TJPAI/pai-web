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

    // Homepage page-top CTAs must render exactly like choosing the same page
    // from the main menu: start at document scroll position 0, not at an
    // in-page anchor offset and never at a remembered destination scroll.
    event.preventDefault();
    event.stopPropagation();
    url.hash='';
    location.assign(url.href);
  },true);
})();
