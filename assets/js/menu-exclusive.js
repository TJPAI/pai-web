(function(){
  'use strict';

  document.addEventListener('click',event=>{
    const target=event.target;
    if(!(target instanceof Element)) return;

    const menuButton=target.closest('.menu-btn');
    if(menuButton){
      const menu=menuButton.closest('.site-header')?.querySelector('.mobile-menu');
      if(menu?.classList.contains('open')){
        const orbitToggle=document.querySelector('.pai-orbit.open .pai-orbit-toggle');
        orbitToggle?.click();
      }
      return;
    }

    const orbitToggle=target.closest('.pai-orbit-toggle');
    if(orbitToggle){
      const orbit=orbitToggle.closest('.pai-orbit');
      const opening=!orbit?.classList.contains('open');
      if(opening){
        const menu=document.querySelector('.site-header .mobile-menu.open');
        const topToggle=document.querySelector('.site-header .menu-btn');
        if(menu&&topToggle) topToggle.click();
      }
    }
  },true);
})();
