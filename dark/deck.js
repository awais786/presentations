(function () {
  var body = document.body;
  var prev = body.getAttribute('data-prev') || '';
  var next = body.getAttribute('data-next') || '';
  var first = body.getAttribute('data-first') || '';
  var last = body.getAttribute('data-last') || '';
  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
      if (next) { e.preventDefault(); window.location.href = next; }
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      if (prev) { e.preventDefault(); window.location.href = prev; }
    } else if (e.key === 'Home') {
      if (first) window.location.href = first;
    } else if (e.key === 'End') {
      if (last) window.location.href = last;
    } else if (e.key === 'f' || e.key === 'F') {
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    }
  });
})();
