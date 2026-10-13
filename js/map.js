(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll('.lesson-card'));
  var years = Array.prototype.slice.call(document.querySelectorAll('.map-year'));
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.f-btn'));
  var count = document.querySelector('.f-count');
  var state = { year: null, letter: null };
  function apply() {
    var shown = 0;
    cards.forEach(function (c) {
      var ok = (!state.year || c.getAttribute('data-year') === state.year) &&
               (!state.letter || c.getAttribute('data-letters').split(' ').indexOf(state.letter) !== -1);
      c.classList.toggle('hidden', !ok);
      if (ok) shown++;
    });
    years.forEach(function (y) {
      y.classList.toggle('hidden', !y.querySelector('.lesson-card:not(.hidden)'));
    });
    buttons.forEach(function (b) {
      var f = b.getAttribute('data-f');
      if (f === 'clear') return;
      b.setAttribute('aria-pressed', state[f] === b.getAttribute('data-v') ? 'true' : 'false');
    });
    count.textContent = (state.year || state.letter) ? 'Showing ' + shown + ' of ' + cards.length + ' lessons' : '';
  }
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-f');
      if (f === 'clear') { state.year = null; state.letter = null; }
      else { var v = b.getAttribute('data-v'); state[f] = state[f] === v ? null : v; }
      apply();
    });
  });
}());
