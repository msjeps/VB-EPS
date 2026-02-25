/**
 * VB EPS — Service Worker
 * Stratégie : Cache-First avec mise à jour en arrière-plan
 * Compatible Android (Chrome) + iOS (Safari 16.4+)
 */

const CACHE_NAME = 'vb-eps-v2';
const CACHE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon_192.png',
  './icon_512.png'
];

/* ── INSTALL : mise en cache initiale ── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CACHE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

/* ── ACTIVATE : nettoyage des anciens caches ── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

/* ── FETCH : Cache-First avec fallback réseau ── */
self.addEventListener('fetch', event => {
  // Ne traiter que les requêtes GET
  if (event.request.method !== 'GET') return;

  // Ignorer les requêtes non-HTTP (extensions, blob, etc.)
  const url = new URL(event.request.url);
  if (!['http:', 'https:'].includes(url.protocol)) return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) {
        // Retourner immédiatement depuis le cache
        // + mettre à jour en arrière-plan si réseau disponible
        const networkFetch = fetch(event.request)
          .then(networkResponse => {
            if (networkResponse && networkResponse.status === 200) {
              const clone = networkResponse.clone();
              caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
            }
            return networkResponse;
          })
          .catch(() => {/* offline, on garde le cache */});
        return cached;
      }

      // Pas en cache : on tente le réseau
      return fetch(event.request)
        .then(networkResponse => {
          if (!networkResponse || networkResponse.status !== 200 || networkResponse.type === 'opaque') {
            return networkResponse;
          }
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return networkResponse;
        })
        .catch(() => {
          // Hors ligne et pas en cache : renvoyer index.html pour les navigations
          if (event.request.mode === 'navigate') {
            return caches.match('./index.html');
          }
          // Sinon réponse vide
          return new Response('', { status: 503, statusText: 'Service Unavailable' });
        });
    })
  );
});

/* ── MESSAGE : forcer la mise à jour depuis l'app ── */
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
