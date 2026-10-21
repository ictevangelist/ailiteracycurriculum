(function () {
  var q = document.getElementById('gl-q'), items = [].slice.call(document.querySelectorAll('.gl-item')),
      secs = [].slice.call(document.querySelectorAll('.gl-year')), btns = [].slice.call(document.querySelectorAll('.gl-filters .f-btn')),
      count = document.getElementById('gl-count'), none = document.getElementById('gl-none'), year = '';
  var m = /^#year-(\d)$/.exec(location.hash); if (m) year = m[1];
  function run() {
    var t = (q.value || '').toLowerCase().trim(), n = 0;
    items.forEach(function (it) {
      var ok = (!year || it.getAttribute('data-year') === year) && (!t || it.getAttribute('data-q').indexOf(t) > -1);
      it.hidden = !ok; if (ok) n++;
    });
    secs.forEach(function (s) { s.hidden = !s.querySelector('.gl-item:not([hidden])'); });
    btns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-v') === year && year ? 'true' : 'false'); });
    count.textContent = (t || year) ? 'Showing ' + n + ' of ' + items.length + ' words' : items.length + ' words';
    none.hidden = n > 0;
  }
  btns.forEach(function (b) { b.addEventListener('click', function () { year = b.getAttribute('data-v'); run(); }); });
  q.addEventListener('input', run);
  window.addEventListener('hashchange', function () { var h = /^#year-(\d)$/.exec(location.hash); if (h) { year = h[1]; run(); } });
  run();
}());
