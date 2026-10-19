var I18N = {
  ru: {
    back: 'Профиль', back_full: '← Вернуться к профилю', nav_focus: 'Направление', nav_teach: 'Преподавание',
    eyebrow: 'Преподавательская деятельность', title: 'Материалы к курсам',
    intro: 'Материалы к курсам, которые я читаю: конспекты, задачи, программы и интерактивные модели. Список пополняется.',
    foot_org: 'Институт гидродинамики им. М. А. Лаврентьева СО РАН · НГУ',
    materials: 'Материалы', empty: 'Материалы к этому курсу пока не добавлены.', term: 'Период'
  },
  en: {
    back: 'Profile', back_full: '← Back to profile', nav_focus: 'Focus', nav_teach: 'Teaching',
    eyebrow: 'Teaching', title: 'Course materials',
    intro: 'Materials for the courses I teach: lecture notes, problem sets, programs and interactive models. The list is growing.',
    foot_org: 'Lavrentyev Institute of Hydrodynamics SB RAS · Novosibirsk State University',
    materials: 'Materials', empty: 'No materials have been added to this course yet.', term: 'Period'
  }
};
var TYPE_ICON = { pdf: 'PDF', slides: 'PPT', code: 'PY', data: 'DAT', video: 'VID', web: 'WEB', link: 'URL' };
function safeHref(h) {
  h = String(h || '');
  if (/^(https?:|mailto:)/i.test(h)) return h;
  if (/^(javascript:|data:|vbscript:)/i.test(h)) return '';
  return IMG_BASE_ROOT + h.replace(/^\//, '');
}
var IMG_BASE_ROOT = (DATA.SITE_BASE || '');
function matHTML(m) {
  var href = safeHref(m.href); if (!href) return '';
  var ext = /^https?:/i.test(href) ? ' target="_blank" rel="noopener"' : '';
  var note = (m.note && m.note[LANG]) ? '<span class="tm-note">' + m.note[LANG] + '</span>' : '';
  return '<a href="' + href + '"' + ext + '><span class="tm-ic tm-ic-' + (TYPE_ICON[m.type] ? m.type : 'file') + '">' + (TYPE_ICON[m.type] || 'FILE') + '</span><span class="tm-t"><span>' + m.title[LANG] + '</span>' + note + '</span><span class="ar">→</span></a>';
}
function render() {
  var T = I18N[LANG];
  applyI18n();
  var name = (DATA.PROFILE && DATA.PROFILE.name[LANG]) || '';
  document.title = (LANG === 'ru' ? 'Материалы к курсам' : 'Course materials') + ' — ' + name;
  var fn = $('#foot-name'); if (fn) fn.textContent = name;
  var list = (DATA.TEACHING_MATERIALS && DATA.TEACHING_MATERIALS.courses) || [];
  $('#tm-list').innerHTML = list.map(function (c, i) {
    var body;
    if (c.groups && c.groups.length) {
      body = '<div class="tm-groups">' + c.groups.map(function (g) {
        var list = (g.materials || []).map(matHTML).join('');
        return '<details class="tm-group"><summary><span class="tm-gt">' + g.title[LANG] + '</span><span class="tm-cnt">' + (g.materials || []).length + '</span></summary><div class="tm-files">' + list + '</div></details>';
      }).join('') + '</div>';
    } else {
      var mats = (c.materials || []).map(matHTML).join('');
      body = mats ? '<div class="tm-files"><div class="flabel">' + T.materials + '</div>' + mats + '</div>' : '<p class="tm-empty">' + T.empty + '</p>';
    }
    return '<article class="tm-course" id="' + (c.id || '') + '"><div class="tm-head"><div class="proj-idx">' + String(i + 1).padStart(2, '0') + ' / ' + String(list.length).padStart(2, '0') + '</div>' +
      '<h2>' + c.title[LANG] + '</h2>' + (c.term ? '<div class="tm-term">' + c.term[LANG] + '</div>' : '') + '</div>' + body + '</article>';
  }).join('');
}
function buildWave() {
  var path = document.querySelector('.wave path'); if (!path) return;
  var W = 1440, H = 220, mid = H * 0.55, d = 'M0 ' + mid;
  for (var x = 0; x <= W; x += 4) { var t = x / W; var y = mid - Math.sin(t * Math.PI * 9) * 90 * Math.exp(-t * 2.4); d += ' L' + x + ' ' + y.toFixed(1); }
  path.setAttribute('d', d);
}
buildWave();
boot();
