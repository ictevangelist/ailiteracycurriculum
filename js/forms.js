(function () {
  var f = document.getElementById('using-form');
  if (!f) return;
  var to = f.getAttribute('data-mailto');
  var msg = f.querySelector('.form-msg');
  f.addEventListener('submit', function (ev) {
    if (f.website && f.website.value) { ev.preventDefault(); return; }
    if (!to) return; // posts to the form service
    ev.preventDefault();
    var lines = [], labels = {name: 'Name', role: 'Role', school: 'School', trust: 'Trust', region: 'Local authority or region',
      year_groups: 'Year groups', heard_about: 'How I heard about it', support: 'Interested in support', email: 'Email'};
    var years = [].slice.call(f.querySelectorAll('input[name=year_groups]:checked')).map(function (x) { return x.value; }).join(', ');
    Object.keys(labels).forEach(function (k) {
      var v = k === 'year_groups' ? years : (k === 'support' ? (f.support.checked ? 'Yes' : 'No') : (f[k] && f[k].value.trim()));
      if (v) lines.push(labels[k] + ': ' + v);
    });
    location.href = 'mailto:' + to + '?subject=' + encodeURIComponent("We're using IDEAL Thinkers") + '&body=' + encodeURIComponent(lines.join('\n'));
    if (msg) msg.textContent = 'Your email app should open with your answers filled in. Press send to finish. Thank you.';
  });
}());
