(function(){
  // язык (RU/EN)
  var root=document.documentElement, KEY='fss-lang';
  function setLang(l){root.lang=l;try{localStorage.setItem(KEY,l)}catch(e){}
    document.querySelectorAll('.lang').forEach(function(b){b.textContent=l==='ru'?'EN':'RU'});
    var t=document.documentElement.dataset['title'+(l==='ru'?'Ru':'En')];if(t)document.title=t;}
  var saved='ru';try{saved=localStorage.getItem(KEY)||'ru'}catch(e){}
  setLang(saved);
  document.querySelectorAll('.lang').forEach(function(b){b.addEventListener('click',function(){setLang(root.lang==='ru'?'en':'ru')})});

  // мобильное меню
  var bg=document.querySelector('.burger'),nav=document.querySelector('nav.main');
  if(bg)bg.addEventListener('click',function(){var o=nav.classList.toggle('open');bg.setAttribute('aria-expanded',o)});

  // появление при прокрутке
  var els=document.querySelectorAll('.rv');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12});
    els.forEach(function(e){io.observe(e)});
  }else els.forEach(function(e){e.classList.add('in')});

  // фильтры тем работ
  var box=document.getElementById('topics');
  if(box){
    var state={area:'all',level:'all'};
    var cards=[].slice.call(box.querySelectorAll('.topic')),empty=document.getElementById('empty');
    function apply(){var n=0;cards.forEach(function(c){
      var ok=(state.area==='all'||c.dataset.area===state.area)&&(state.level==='all'||!c.dataset.level||c.dataset.level.split(' ').indexOf(state.level)>-1);
      c.hidden=!ok;if(ok)n++});empty.style.display=n?'none':'block'}
    document.querySelectorAll('.chip').forEach(function(ch){ch.addEventListener('click',function(){
      var g=ch.dataset.group;state[g]=ch.dataset.val;
      document.querySelectorAll('.chip[data-group="'+g+'"]').forEach(function(x){x.classList.toggle('on',x===ch)});apply()})});
    // поиск по хэшу: topics.html#gasdyn
    var h=location.hash.slice(1);if(h){var c=document.querySelector('.chip[data-val="'+h+'"]');if(c)c.click()}
  }

  // просмотр фотографий галереи в полном размере
  document.querySelectorAll('.gallery img, .news-img').forEach(function(im){
    im.addEventListener('click',function(){
      var o=document.createElement('div');o.className='lightbox';
      var big=document.createElement('img');big.src=im.src;big.alt=im.alt;o.appendChild(big);
      function close(){o.remove();document.removeEventListener('keydown',key)}
      function key(e){if(e.key==='Escape')close()}
      o.addEventListener('click',close);document.addEventListener('keydown',key);document.body.appendChild(o);
    });
  });
})();
