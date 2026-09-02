// Automatisch erzeugt – nicht von Hand bearbeiten.
const V = 'suedafrika-147b2c9dcf';
const SHELL = ['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png',
               './reise.ics','./docs/sars-reiseerklaerung.pdf',
               './data/Suedafrika_Restaurants_und_Aktivitaeten.csv'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL).catch(()=>{})).then(()=>self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks =>
    Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const font = url.host === 'fonts.googleapis.com' || url.host === 'fonts.gstatic.com';

  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => {
      const cp = r.clone(); caches.open(V).then(c => c.put('./index.html', cp)); return r;
    }).catch(() => caches.match('./index.html').then(r => r || caches.match('./'))));
    return;
  }
  if (font) {
    e.respondWith(caches.match(req).then(hit => {
      const net = fetch(req).then(r => { const cp = r.clone(); caches.open(V).then(c => c.put(req, cp)); return r; }).catch(()=>hit);
      return hit || net;
    }));
    return;
  }
  if (url.origin === location.origin) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
      const cp = r.clone(); caches.open(V).then(c => c.put(req, cp)); return r;
    }).catch(()=>hit)));
  }
});
