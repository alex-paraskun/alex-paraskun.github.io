(function () {
  var data = window.COURSE_MATERIALS || {};
  var icons = { pdf: 'PDF', slides: 'PPT', code: 'PY', data: 'DAT', video: 'VID', link: 'URL' };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function safeUrl(u) { u = String(u || ''); return /^(https?:|mailto:|materials\/)/i.test(u) ? u : ''; }
  document.querySelectorAll('details.materials').forEach(function (d) {
    var list = (data[d.getAttribute('data-course')] || []).filter(function (m) { return safeUrl(m.url); });
    var body = d.querySelector('.mat-body'), cnt = d.querySelector('.cnt');
    cnt.textContent = '(' + list.length + ')';
    if (!list.length) {
      body.innerHTML = '<p class="mat-empty"><span class="t-ru">Материалы пока не добавлены.</span><span class="t-en">No materials yet.</span></p>';
      return;
    }
    body.innerHTML = '<ul class="mat-list">' + list.map(function (m) {
      var url = safeUrl(m.url); if (!url) return '';
      var ext = /^https?:/i.test(url) ? ' target="_blank" rel="noopener"' : '';
      var ru = esc(m.title), en = esc(m.titleEn || m.title);
      return '<li><span class="ico">' + (icons[m.type] || 'FILE') + '</span><a href="' + esc(url) + '"' + ext + '><span class="t-ru">' + ru + '</span><span class="t-en">' + en + '</span></a>' +
        (m.date ? '<span class="mat-date">' + esc(m.date) + '</span>' : '') +
        (m.note ? '<span class="mat-note">' + esc(m.note) + '</span>' : '') + '</li>';
    }).join('') + '</ul>';
  });
  // переход по ссылке вида courses.html#c-gasdyn-1: открыть блок материалов
  var h = location.hash.slice(1), el = h && document.getElementById(h);
  if (el) { var d = el.querySelector('details.materials'); if (d) d.open = true; }
})();
