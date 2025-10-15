const CACHE_NAME = 'cse-hub-cache-v1';
// Add the paths to your core files here.
const urlsToCache = [
  '/',
  '/index.html',
  '/style.css',
  '/script.js',
  '/profile.js',
  '/preview.js',
  '/contribute.html',
  '/contribution_handler.js'
  // Add other essential assets like a logo if you have one
];

// Install the service worker and cache the static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Serve cached content when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
