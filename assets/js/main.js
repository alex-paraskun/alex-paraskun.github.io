var I18N = {
  ru: {
    brand: 'ПАРАСКУН <b>А.Г.</b>', nav_focus: 'Направление', nav_edu: 'Образование', nav_pubs: 'Публикации',
    nav_teach: 'Преподавание', nav_activity: 'Деятельность', nav_projects: 'Проекты →',
    edu_h: 'Образование и должность', qual_h: 'Квалификационные работы', aff_h: 'Аффилиации',
    art_h: 'Статьи в журналах', proc_h: 'Статьи в сборниках', abs_h: 'Тезисы докладов', book_h: 'Книги',
    conf_h: 'Доклады на конференциях', misc_h: 'Препринты и выступления в СМИ', teach_h: 'Преподавание курсов',
    activity_h: 'Деятельность', rev_h: 'Экспертные заключения', abs_show: 'Аннотация', abs_hide: 'Свернуть',
    foot_org: 'Институт гидродинамики им. М. А. Лаврентьева СО РАН · НГУ',
    foot_note: 'Данные профиля по состоянию на 2026 г. Источник — научная информационная система SciAct (ИГиЛ СО РАН).',
    more: 'Показать все', less: 'Свернуть', supervisor: 'Руководитель', hours: 'часов', sem: 'семинары', prac: 'практикум'
  },
  en: {
    brand: 'PARASKUN <b>A.G.</b>', nav_focus: 'Focus', nav_edu: 'Education', nav_pubs: 'Publications',
    nav_teach: 'Teaching', nav_activity: 'Activity', nav_projects: 'Projects →',
    edu_h: 'Education & position', qual_h: 'Qualification works', aff_h: 'Affiliations',
    art_h: 'Journal articles', proc_h: 'Proceedings papers', abs_h: 'Conference abstracts', book_h: 'Books',
    conf_h: 'Conference reports', misc_h: 'Preprints & media appearances', teach_h: 'Teaching',
    activity_h: 'Activity', rev_h: 'Peer reviews', abs_show: 'Abstract', abs_hide: 'Collapse',
    foot_org: 'Lavrentyev Institute of Hydrodynamics SB RAS · Novosibirsk State University',
    foot_note: 'Profile data as of 2026. Source — SciAct research information system (LIH SB RAS).',
    more: 'Show all', less: 'Collapse', supervisor: 'Supervisor', hours: 'hours', sem: 'seminars', prac: 'lab practicum'
  }
};

function hl(s) { return (s || '').replace(/\*\*(.+?)\*\*/g, '<span class="hl">$1</span>'); }

function pubHTML(p, i) {
  var T = I18N[LANG];
  var au = p.au ? ('<div class="pub-authors">' + markMe(p.au[LANG]) + '</div>') : '';
  var footInner = badges(p.db) + doiLink(p.doi);
  if (p.abs) footInner += '<button class="abs-toggle" onclick="toggleAbs(this)">▸ ' + T.abs_show + '</button>';
  var foot = footInner ? ('<div class="pub-foot">' + footInner + '</div>') : '';
  var abstract = '';
  if (p.abs) {
    var txt = (p.abs.text && p.abs.text[LANG]) ? '<p>' + p.abs.text[LANG] + '</p>' : '';
    var ph = (p.abs.photos && p.abs.photos.length) ? carouselHTML(p.abs.photos) : '';
    abstract = '<div class="pub-abstract">' + txt + ph + '</div>';
  }
  return '<div class="pub"><div class="pub-n">' + (i + 1) + '</div><div class="pub-body">' +
    '<div class="pub-title">' + p.t[LANG] + '</div>' + au + '<div class="pub-venue">' + p.v[LANG] + '</div>' + foot + abstract + '</div></div>';
}

function render() {
  var T = I18N[LANG];
  applyI18n();
  var P = DATA.PROFILE || { name: {}, eyebrow: {}, role: {}, ids: {} };
  document.title = P.name[LANG] || 'Профиль';

  $$('[data-bind]').forEach(function (el) {
    var k = el.dataset.bind;
    if (k === 'name') el.textContent = P.name[LANG];
    else if (k === 'eyebrow') el.textContent = P.eyebrow[LANG];
    else if (k === 'role') el.textContent = P.role[LANG];
    else if (k === 'focus_h') el.textContent = (DATA.FOCUS && DATA.FOCUS.h[LANG]) || '';
    else if (k === 'focus_text') el.innerHTML = hl(DATA.FOCUS && DATA.FOCUS.text[LANG]);
  });

  $('#hero-photo').innerHTML = '<img src="' + IMG(P.photo) + '" alt="' + (P.name[LANG] || '') + '">';
  var ids = P.ids || {};
  var chips = '';
  if (ids.ORCID) chips += '<a class="chip" href="https://orcid.org/' + ids.ORCID + '" target="_blank" rel="noopener"><span class="k">ORCID</span> ' + ids.ORCID + '</a>';
  if (ids.Scopus) chips += '<a class="chip" href="https://www.scopus.com/authid/detail.uri?authorId=' + ids.Scopus + '" target="_blank" rel="noopener"><span class="k">Scopus</span> ' + ids.Scopus + '</a>';
  if (ids.ResearcherID) chips += '<span class="chip"><span class="k">ResearcherID</span> ' + ids.ResearcherID + '</span>';
  if (ids['РИНЦ']) chips += '<span class="chip"><span class="k">РИНЦ</span> ' + ids['РИНЦ'] + '</span>';
  if (ids.Email) chips += '<a class="chip" href="mailto:' + ids.Email + '"><span class="k">@</span> ' + ids.Email + '</a>';
  $('#hero-meta').innerHTML = chips;
  $('#foot-links').innerHTML =
    (ids.Email ? '<a href="mailto:' + ids.Email + '">' + ids.Email + '</a>' : '') +
    (ids.ORCID ? '<a href="https://orcid.org/' + ids.ORCID + '" target="_blank" rel="noopener">ORCID ' + ids.ORCID + '</a>' : '') +
    (ids.Scopus ? '<a href="https://www.scopus.com/authid/detail.uri?authorId=' + ids.Scopus + '" target="_blank" rel="noopener">Scopus ' + ids.Scopus + '</a>' : '');

  // stats
  var A = function (x) { return (x || []).length; };
  var stats = [
    { n: A(DATA.ARTICLES), l: { ru: 'статьи в журналах', en: 'journal articles' } },
    { n: A(DATA.ABSTRACTS), l: { ru: 'тезисы докладов', en: 'abstracts' } },
    { n: A(DATA.CONF), l: { ru: 'доклады', en: 'conf. reports' } },
    { n: A(DATA.BOOKS), l: { ru: 'книги', en: 'books' } },
    { n: A(DATA.REVIEWS), l: { ru: 'рецензии', en: 'peer reviews' } },
    { n: (P.citations || 0), l: { ru: 'цитирования OpenAlex', en: 'OpenAlex citations' } }
  ];
  $('#readout').innerHTML = stats.map(function (s) { return '<div class="stat"><div class="n">' + s.n + '</div><div class="l">' + s.l[LANG] + '</div></div>'; }).join('');

  // education
  var edu = '';
  (DATA.EDU || []).forEach(function (e) {
    if (e.position) edu += '<div class="card"><div class="sub">' + e.title[LANG] + '</div><h3>' + e.lab[LANG] + '</h3><div class="txt">' + e.org[LANG] + '</div></div>';
    else edu += '<div class="card"><div class="sub">' + e.year + '</div><h3>' + e.deg[LANG] + '</h3><div class="txt">' + e.org[LANG] + '</div></div>';
  });
  $('#edu-grid').innerHTML = edu;

  $('#qual-list').innerHTML = (DATA.QUALS || []).map(function (q, i) { return '<li><span class="idx">' + String(i + 1).padStart(2, '0') + '</span><div><div class="t">' + q.t[LANG] + '</div><div class="m">' + q.deg[LANG] + ' · ' + q.year + ' · ' + T.supervisor + ': ' + q.sup + '</div></div></li>'; }).join('');
  $('#aff-grid').innerHTML = (DATA.AFF || []).map(function (a) { return '<div class="card"><div class="sub">' + a.abbr + '</div><h3>' + a.org[LANG] + '</h3><div class="txt">' + a.d[LANG] + '</div><span class="tag">' + a.period + '</span></div>'; }).join('');

  $('#articles-list').innerHTML = (DATA.ARTICLES || []).map(pubHTML).join('');
  $('#proc-list').innerHTML = (DATA.PROC || []).map(pubHTML).join('');
  $('#abs-list').innerHTML = (DATA.ABSTRACTS || []).map(pubHTML).join('');
  $('#book-list').innerHTML = (DATA.BOOKS || []).map(pubHTML).join('');
  $('#conf-list').innerHTML = (DATA.CONF || []).map(function (c, i) { var au = c.au ? ('<div class="pub-authors">' + markMe(c.au[LANG]) + '</div>') : ''; return '<div class="pub"><div class="pub-n">' + (i + 1) + '</div><div class="pub-body"><div class="pub-title">' + c.t[LANG] + '</div>' + au + '<div class="pub-venue">' + c.v[LANG] + '</div></div></div>'; }).join('');
  $('#preprint-list').innerHTML = (DATA.PREPRINT || []).map(pubHTML).join('');
  $('#media-list').innerHTML = (DATA.MEDIA || []).map(function (m, i) { return '<li><span class="idx">' + String(i + 1).padStart(2, '0') + '</span><div><div class="t">' + m.t[LANG] + '</div><div class="m">' + m.m[LANG] + '</div></div></li>'; }).join('');

  // teaching
  var TE = DATA.TEACHING || { items: [], photos: [] };
  $('#teach-list').innerHTML = (TE.items || []).map(function (t, i) { return '<li><span class="idx">' + String(i + 1).padStart(2, '0') + '</span><div><div class="t">' + t.c[LANG] + '</div><div class="m">' + t.term[LANG] + ' · ' + T[t.type] + ' · ' + t.h + ' ' + T.hours + '</div></div></li>'; }).join('');
  var tph = TE.photos || [];
  if (tph.length) { $('#teach-carousel').innerHTML = carouselHTML(tph); $('#teach-wrap').classList.remove('no-photos'); }
  else { $('#teach-carousel').innerHTML = ''; $('#teach-wrap').classList.add('no-photos'); }

  // activity
  $('#act-list').innerHTML = (DATA.ACTIVITY || []).map(function (a) { return '<div class="act">' + carouselHTML(a.photos) + '<div class="act-cap"><h3>' + a.title[LANG] + '</h3><p>' + a.caption[LANG] + '</p></div></div>'; }).join('');

  $('#rev-list').innerHTML = (DATA.REVIEWS || []).map(function (r, i) { return '<li class="pub"><div class="pub-n">' + (i + 1) + '</div><div class="pub-body"><div class="pub-title" style="font-size:1rem">' + r.t[LANG] + '</div><div class="pub-venue" style="margin-top:6px">' + r.j + '</div></div></li>'; }).join('');

  var setc = function (id, arr) { var el = document.getElementById(id); if (el) el.textContent = '[' + (arr || []).length + ']'; };
  setc('art-c', DATA.ARTICLES); setc('proc-c', DATA.PROC); setc('abs-c', DATA.ABSTRACTS); setc('book-c', DATA.BOOKS);
  setc('conf-c', DATA.CONF); setc('teach-c', TE.items); setc('rev-c', DATA.REVIEWS);
  $$('.morebtn').forEach(function (b) { var w = document.getElementById(b.dataset.target); b.textContent = w.classList.contains('collapsed') ? T.more : T.less; });

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
