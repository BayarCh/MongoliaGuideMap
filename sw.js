const CACHE_NAME = 'travelmap-v79';

const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo192.png',
  '/logo512.png',
  '/logo180.png',
  '/logo1200x630.png',
  '/favicon.ico'
];

// 1. Суурилуулах (Install) - Шинэ хувилбарыг шууд идэвхжүүлнэ
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.all(
        urlsToCache.map(url => cache.add(url).catch(err => console.log('Файл татахад алдаа: ' + url)))
      );
    })
  );
});

// 2. Идэвхжүүлэх (Activate) - Хуучин кэшийг шууд устгах
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
    }).then(() => self.clients.claim())
  );
});

// 3. Мэдээлэл татах (Fetch) - Хамгийн чухал хэсэг!
// Эхлээд серверээс (Network) шалгана, сүлжээгүй бол кэшээс уншина.
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        return response; // Сервер ажиллаж байвал шинэ мэдээллийг өгнө.
      })
      .catch(() => {
        return caches.match(event.request); // Сүлжээгүй үед л кэшээ ашиглана.
      })
  );
});