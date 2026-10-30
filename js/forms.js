(function () {
  var f = document.getElementById('using-form');
  if (!f) return;
  var to = f.getAttribute('data-mailto');
  var msg = f.querySelector('.form-msg');
  var btn = f.querySelector('button[type=submit]');
  var failed = 'Sorry, that did not send. Please try again, or email mark@ictevangelist.com.';
  function checked(name) {
    return [].slice.call(f.querySelectorAll('input[name="' + name + '"]:checked')).map(function (x) { return x.value; }).join(', ');
  }
  f.addEventListener('submit', function (ev) {
    ev.preventDefault();
    if (f.website && f.website.value) return;
    if (to) {
      var lines = [], labels = {your_name: 'Name', role: 'Role', school: 'School', trust: 'Trust', region: 'Local authority or region',
        year_groups: 'Year groups', heard_about: 'How I heard about it', support: 'Interested in support', email: 'Email'};
      Object.keys(labels).forEach(function (k) {
        var v = k === 'year_groups' ? checked('year_groups[]') : (k === 'support' ? (checked('support[]') ? 'Yes' : 'No') : (f[k] && f[k].value.trim()));
        if (v) lines.push(labels[k] + ': ' + v);
      });
      location.href = 'mailto:' + to + '?subject=' + encodeURIComponent("We're using IDEAL Thinkers") + '&body=' + encodeURIComponent(lines.join('\n'));
      msg.textContent = 'Your email app should open with your answers filled in. Press send to finish. Thank you.';
      return;
    }
    // sends to the Contact Form 7 form on ictevangelist.com, which emails the answers to Mark
    btn.disabled = true;
    msg.textContent = 'Sending...';
    fetch(f.action, {method: 'POST', body: new FormData(f)})
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.status === 'mail_sent') {
          f.reset(); msg.textContent = 'Thank you. Your answers have been sent.';
          // counts a sent form in Google Analytics; form_start alone only shows someone began typing
          if (window.gtag) gtag('event', 'sign_up', {method: 'using_it_form'});
        }
        else if (d.status === 'validation_failed' && d.invalid_fields && d.invalid_fields.length) {
          msg.textContent = 'Please check the form: ' + d.invalid_fields.map(function (x) { return x.message; }).join(' ');
        } else msg.textContent = failed;
      })
      .catch(function () { msg.textContent = failed; })
      .then(function () { btn.disabled = false; if (window.turnstile) window.turnstile.reset(); });
  });
}());
