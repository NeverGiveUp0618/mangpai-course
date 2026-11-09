/* 网络优先——微信 X5 缓存顽固，保持与其余站一致。 */
var C = 'mangpai-course-v33';
var CORE = ['./', 'index.html', 'style.css', 'app.js', 'data/data-meta.js', 'data/data-course.js', 'data/data-notes.js'];
self.addEventListener('install', function (e) {
  self.skipWaiting();
  e.waitUntil(caches.open(C).then(function (c) { return c.addAll(CORE).catch(function () {}); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.map(function (k) { return k === C ? null : caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  /* cacheFirstData：data/*.js?v=<构建时间> 的 URL 一版内容永不变，缓存优先——弱网下不必等网络超时再回退 */
  if (/\/data\/[^?]+\.js\?v=/.test(e.request.url)) {
    e.respondWith(caches.match(e.request).then(function (hit) {
      if (hit) return hit;
      return fetch(e.request).then(function (r) {
        var cp = r.clone();
        caches.open(C).then(function (c) { c.put(e.request, cp); });
        return r;
      }).catch(function () { return caches.match(e.request, { ignoreSearch: true }); });
    }));
    return;
  }
  e.respondWith(
    fetch(e.request).then(function (r) {
      var cp = r.clone();
      caches.open(C).then(function (c) { c.put(e.request, cp); });
      return r;
    }).catch(function () { return caches.match(e.request, { ignoreSearch: true }); })
  );
});
