/* ===== shared helpers (both pages) ===== */
var $ = function (s) { return document.querySelector(s); };
var $$ = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };
var LANG = 'ru';

var ME = ['Параскун А.Г.', 'Параскун А.', 'ПАРАСКУН А.Г.', 'Paraskun A.G.', 'Paraskun A.', 'Alexandr Paraskun', 'Paraskun A'];
function markMe(str) { var o = str || ''; ME.forEach(function (n) { o = o.split(n).join('<span class="me">' + n + '</span>'); }); return o; }
function badges(db) { return (db || []).map(function (b) { return '<span class="badge">' + b + '</span>'; }).join(''); }
function doiLink(d) { return d ? '<a class="doi" href="https://doi.org/' + d + '" target="_blank" rel="noopener">DOI ' + d + '</a>' : ''; }

/* filename -> image URL (Jekyll baseurl aware). Absolute/URL/data left as-is. */
function IMG(name) {
  if (!name) return '';
  if (/^(https?:|data:|\/|\.\.?\/)/.test(name)) return name;
  return ((typeof DATA !== 'undefined' && DATA.IMG_BASE) || '') + name;
}

function setLang(l) { LANG = l; try { localStorage.setItem('site_lang', l); } catch (e) {} render(); }
function toggleMore(btn) {
  var wrap = document.getElementById(btn.dataset.target);
  wrap.classList.toggle('collapsed');
  btn.textContent = wrap.classList.contains('collapsed') ? I18N[LANG].more : I18N[LANG].less;
}
function toggleAbs(btn) {
  var panel = btn.closest('.pub-body').querySelector('.pub-abstract');
  var open = panel.classList.toggle('open');
  btn.innerHTML = (open ? '▾ ' : '▸ ') + (open ? I18N[LANG].abs_hide : I18N[LANG].abs_show);
}

/* carousels: rebuilt after every render */
function initCarousels() {
  $$('.carousel').forEach(function (car) {
    var track = car.querySelector('.c-track');
    var imgs = track.children.length;
    if (imgs <= 1) { car.classList.add('single'); return; }
    var i = 0;
    var dots = car.querySelector('.c-dots');
    var go = function (n) {
      i = (n + imgs) % imgs;
      track.style.transform = 'translateX(-' + (i * 100) + '%)';
      if (dots) dots.querySelectorAll('span').forEach(function (d, k) { d.classList.toggle('on', k === i); });
    };
    car.querySelector('.prev').onclick = function () { go(i - 1); };
    car.querySelector('.next').onclick = function () { go(i + 1); };
    if (dots) dots.querySelectorAll('span').forEach(function (d, k) { d.onclick = function () { go(k); }; });
    go(0);
  });
}
function carouselHTML(photos) {
  photos = photos || [];
  var imgs = photos.map(function (src) { return '<img src="' + IMG(src) + '" alt="" loading="lazy">'; }).join('');
  var dots = photos.map(function () { return '<span></span>'; }).join('');
  var single = photos.length <= 1 ? ' single' : '';
  return '<div class="carousel' + single + '"><div class="c-track">' + imgs + '</div>' +
    '<button class="c-nav prev" aria-label="Prev">‹</button>' +
    '<button class="c-nav next" aria-label="Next">›</button>' +
    '<div class="c-dots">' + dots + '</div></div>';
}

function applyI18n() {
  var T = I18N[LANG];
  document.documentElement.lang = LANG;
  $$('[data-i18n]').forEach(function (el) { if (T[el.dataset.i18n] !== undefined) el.innerHTML = T[el.dataset.i18n]; });
  $$('.langswitch button').forEach(function (b) { b.classList.toggle('active', b.dataset.lang === LANG); });
}
function boot() { try { var s = localStorage.getItem('site_lang'); if (s) LANG = s; } catch (e) {} render(); }
