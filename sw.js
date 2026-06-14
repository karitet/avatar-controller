// Avatar Controller — minimal offline app shell.
// The app itself loads offline; the live P2P link still needs a network for pairing/STUN.
const CACHE = "avatar-controller-v5";
const CMDS = ["forward","backward","left","right","stop","shoot","pickup"];
const LANGS = ["da","en"];
const SHELL = [
  "./", "./index.html", "./manifest.webmanifest", "./icon.svg",
  "./vendor/peerjs.min.js", "./vendor/qrcode.js",
  ...LANGS.flatMap(l => CMDS.map(c => `./audio/${l}/${c}.mp3`))
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).catch(() => caches.match("./index.html")))
  );
});
