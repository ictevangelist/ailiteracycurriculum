(function () {
  var d = document.createElement('dialog');
  d.className = 'zoom-box';
  d.innerHTML = '<button type="button" class="btn zoom-close">Close</button><img alt="">';
  document.body.appendChild(d);
  var img = d.querySelector('img');
  d.querySelector('.zoom-close').addEventListener('click', function () { d.close(); });
  d.addEventListener('click', function (ev) { if (ev.target === d) d.close(); });
  [].forEach.call(document.querySelectorAll('a.zoom'), function (a) {
    a.addEventListener('click', function (ev) {
      if (!d.showModal) return;
      ev.preventDefault();
      var src = a.querySelector('img');
      img.src = a.href;
      img.alt = src.alt;
      d.showModal();
    });
  });
}());
