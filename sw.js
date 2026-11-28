/* Legacy Service Worker retirement stub. */
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('pai-site-')).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
