var I18N = {
  ru: {
    back: 'Профиль', back_full: '← Вернуться к профилю', nav_focus: 'Направление', nav_pubs: 'Публикации',
    eyebrow: 'Исследовательские проекты', title: 'Проекты',
    intro: 'Ключевые направления работы: от импульсной рентгеновской техники до численного моделирования волновых процессов. К каждому проекту — фотографии и ссылки на публикации.',
    files: 'Публикации и файлы', foot_org: 'Институт гидродинамики им. М. А. Лаврентьева СО РАН · НГУ',
    more: 'Показать все', less: 'Свернуть', abs_show: 'Аннотация', abs_hide: 'Свернуть'
  },
  en: {
    back: 'Profile', back_full: '← Back to profile', nav_focus: 'Focus', nav_pubs: 'Publications',
    eyebrow: 'Research projects', title: 'Projects',
    intro: 'Key lines of work, from pulsed X-ray technology to numerical modelling of wave processes. Each project comes with photos and links to publications.',
    files: 'Publications & files', foot_org: 'Lavrentyev Institute of Hydrodynamics SB RAS · Novosibirsk State University',
    more: 'Show all', less: 'Collapse', abs_show: 'Abstract', abs_hide: 'Collapse'
  }
};

function fileHTML(f) {
  return '<a href="' + f.href + '" target="_blank" rel="noopener"><span class="ic">↓</span><span>' + f.label + '</span><span class="ar">→</span></a>';
}
function render() {
  var T = I18N[LANG];
  applyI18n();
  var name = (DATA.PROFILE && DATA.PROFILE.name[LANG]) || '';
  document.title = (LANG === 'ru' ? 'Проекты' : 'Projects') + ' — ' + name;
  var fn = $('#foot-name'); if (fn) fn.textContent = name;
  var list = DATA.PROJECTS || [];
  $('#proj-list').innerHTML = list.map(function (p, i) {
    var files = (p.files && p.files.length) ?
      '<div class="proj-files"><div class="flabel">' + T.files + '</div>' + p.files.map(fileHTML).join('') + '</div>' : '';
    return '<article class="proj">' + carouselHTML(p.photos) +
      '<div class="proj-body"><div class="proj-idx">' + String(i + 1).padStart(2, '0') + ' / ' + String(list.length).padStart(2, '0') + '</div>' +
      '<h2>' + p.title[LANG] + '</h2><p class="proj-desc">' + p.desc[LANG] + '</p>' + files + '</div></article>';
  }).join('');
  initCarousels();
}

function buildWave() {
  var path = document.querySelector('.wave path'); if (!path) return;
  var W = 1440, H = 220, mid = H * 0.55, d = 'M0 ' + mid;
  for (var x = 0; x <= W; x += 4) { var t = x / W; var y = mid - Math.sin(t * Math.PI * 9) * 90 * Math.exp(-t * 2.4); d += ' L' + x + ' ' + y.toFixed(1); }
  path.setAttribute('d', d);
}
buildWave();
boot();
