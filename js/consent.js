(function () {
  var s = document.currentScript, id = s.getAttribute('data-ga'), key = 'ideal-analytics';
  var box = document.querySelector('.consent');
  function get() { try { return localStorage.getItem(key); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(key, v); } catch (e) {} }
  function load() {
    if (window.gtag) return;
    var g = document.createElement('script');
    g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(g);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', id, { allow_google_signals: false, allow_ad_personalization_signals: false });
  }
  function clear() {
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim();
      if (n.indexOf('_ga') === 0) document.cookie = n + '=; Max-Age=0; path=/; domain=.' + location.hostname.split('.').slice(-2).join('.');
      if (n.indexOf('_ga') === 0) document.cookie = n + '=; Max-Age=0; path=/';
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-consent]'), function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-consent');
      var was = get();
      set(v); box.hidden = true;
      if (v === 'yes') load();
      else { clear(); if (was === 'yes') location.reload(); }
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll('[data-consent-open]'), function (b) {
    b.addEventListener('click', function () { box.hidden = false; box.querySelector('button').focus(); });
  });
  var v = get();
  if (v === 'yes') load(); else if (v !== 'no') box.hidden = false;
}());
