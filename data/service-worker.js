const CACHE_NAME = 'travelmap-v72'; // Хувилбарыг ахиулснаар хөтөч шинэчлэлтийг танина
const assets = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo192.png',
  '/logo512.png',
  '/logo180.png',
  '/logo1200x630.png',
  '/favicon.ico'
];

// Суулгах үе шат
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('Кэш нээгдлээ');
      // addAll-ийн оронд илүү найдвартай аргаар нэмэх
      return Promise.all(
        assets.map(url => {
          return cache.add(url).catch(err => console.warn('Файл кэшлэхэд алдаа: ' + url));
        })
      );
    })
  );
});

// Дата татах үе шат (Офлайн үед ажиллах боломж олгоно)
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

// Хуучин кэшийг цэвэрлэх үе шат
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});