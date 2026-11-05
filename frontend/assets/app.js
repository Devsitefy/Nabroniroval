'use strict';

// Важное: все запросы идут на тот же origin, что и сайт.
// Nginx проксирует /hotels, /auth и /bookings в FastAPI.
const state = {
  user: null,
  search: null,
  searchResults: [],
  searchPage: 1,
  perPage: 9,
  searchPending: false,
  token: 0,
  afterLogin: null,
};
const app = document.querySelector('#app');
const dialog = document.querySelector('#confirm-dialog');
const toastArea = document.querySelector('#toast-area');
const currency = new Intl.NumberFormat('ru-RU');

const iconPaths = {
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  pin: '<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',
  arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>',
  back: '<path d="M20 12H4m6 6-6-6 6-6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  shield: '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-4"/>',
  spark: '<path d="m12 3 1.9 6.1L20 11l-6.1 1.9L12 19l-1.9-6.1L4 11l6.1-1.9L12 3Z"/>',
  heart: '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V10Z"/><path d="M9 21v-8h6v8"/>',
  bed: '<path d="M3 18v-7m18 7v-7M3 15h18v4H3zM5 15V9a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v6"/><path d="M5 12h14"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 11v6m0-10h.01"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a16 16 0 0 1 0 18M12 3a16 16 0 0 0 0 18"/>',
  lock: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  logout: '<path d="M9 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h4M16 17l5-5-5-5m5 5H9"/>',
  alert: '<path d="m12 3 10 18H2L12 3Z"/><path d="M12 9v5m0 3h.01"/>',
  close: '<path d="M18 6 6 18M6 6l12 12"/>',
  suitcase: '<rect x="4" y="7" width="16" height="14" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M8 7v14m8-14v14"/>',
  sliders: '<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="2" fill="white"/><circle cx="15" cy="17" r="2" fill="white"/>',
};
function ic(name, cls = '') { return `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.info}</svg>`; }
function esc(v) { return String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function rub(n) { return `${currency.format(Number(n) || 0)} ₽`; }
function isoDate(d) { const y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),day=String(d.getDate()).padStart(2,'0');return `${y}-${m}-${day}`; }
function shiftDays(date, count) { const d=new Date(`${date}T12:00:00`);d.setDate(d.getDate()+count);return isoDate(d); }
function today() { return isoDate(new Date()); }
function nights(from,to) { return Math.max(0,Math.round((Date.parse(to+'T12:00:00Z')-Date.parse(from+'T12:00:00Z'))/86400000)); }
function dateText(date) { try{return new Intl.DateTimeFormat('ru-RU',{day:'numeric',month:'short',year:'numeric'}).format(new Date(date+'T12:00:00'));}catch{return esc(date);} }
function searchDefaults() { const from=shiftDays(today(),1);return {location:'',title:'',date_from:from,date_to:shiftDays(from,3)}; }
function parseRoute() {const raw=location.hash.slice(1)||'/';const pos=raw.indexOf('?');return {path:pos<0?raw:raw.slice(0,pos),query:new URLSearchParams(pos<0?'':raw.slice(pos+1))};}
function routeSearchParams(search) {return new URLSearchParams(Object.entries(search).filter(([_,v])=>v!=null&&v!=='' )).toString();}
function detailHref(id,search=state.search||searchDefaults()) {return `#/hotel/${encodeURIComponent(id)}?${routeSearchParams({date_from:search.date_from,date_to:search.date_to})}`;}
function go(hash) { if(location.hash===hash) render();else location.hash=hash; }
function toast(message,error=false) {const el=document.createElement('div');el.className=`toast ${error?'error':''}`;el.innerHTML=ic(error?'alert':'check')+`<span>${esc(message)}</span>`;toastArea.appendChild(el);setTimeout(()=>el.remove(),5500);}
async function request(url,options={}) {
  const init={credentials:'same-origin',...options};
  if(init.body && !(init.body instanceof FormData))init.headers={...init.headers,'Content-Type':'application/json'};
  let response;
  try { response=await fetch(url,init); }
  catch { throw new Error('Не удалось подключиться к серверу. Проверь Nginx и FastAPI.'); }
  const ct=response.headers.get('content-type')||'';
  const data=ct.includes('application/json') ? await response.json().catch(()=>null) : null;
  if(!response.ok){
    let msg=data?.detail;
    if(Array.isArray(msg))msg=msg.map(x=>x.msg).filter(Boolean).join('; ');
    const err=new Error(typeof msg==='string'?msg:`Ошибка сервера: HTTP ${response.status}`);
    err.status=response.status;throw err;
  }
  return data;
}
function imageURL(raw) {
  if(!raw || typeof raw!=='string')return null;
  // API хранит src/static/images/<имя>. Nginx раздаёт ту же папку под /media/.
  const filename=raw.replaceAll('\\','/').split('/').pop();
  if(!filename || filename==='.' || filename==='..')return null;
  return '/media/'+encodeURIComponent(filename);
}
function roomImage(room) {const first=room?.images?.[0];return imageURL(first?.image_1024||first?.image_512||first?.image_256);}
function cover(image,extra='') {return image?`<img class="${extra}" src="${esc(image)}" alt="Фотография номера" loading="lazy" data-image-fallback>`:`<div class="cover-placeholder"><img src="/assets/placeholder.svg" alt="Иллюстрация отеля" loading="lazy"></div>`;}
function navHTML(){const logged=!!state.user;return `<header class="site-header"><div class="wrap header-inner">
<a class="brand" href="#/" aria-label="Набронировал — главная"><span class="brand-mark">Н</span><span>набронировал<span style="color:#dc9d76">.</span></span></a>
<nav class="header-nav" aria-label="Навигация"><a href="#/">Найти жильё</a><a href="#/bookings">Мои бронирования</a><a href="/docs" target="_blank" rel="noopener">API / Docs</a></nav>
<div class="header-actions">${logged?`<span class="user-chip" title="${esc(state.user.email)}"><span class="user-avatar">${esc(state.user.email?.[0]?.toUpperCase()||'U')}</span><span>${esc(state.user.email)}</span></span><button class="btn btn-soft btn-small" type="button" data-logout title="Выйти">${ic('logout','icon-sm')}<span>Выйти</span></button>`:`<a class="btn btn-soft btn-small" href="#/login">Войти</a><a class="btn btn-primary btn-small" href="#/register">Регистрация</a>`}</div></div></header>`;}
function footerHTML(){return `<footer class="site-footer"><div class="wrap"><div class="footer-top"><div class="footer-brand"><a class="brand" href="#/"><span class="brand-mark">Н</span><span>набронировал.</span></a><p>Находи подходящее жильё, выбирай даты и бронируй без лишних шагов.</p></div><div class="footer-links"><a href="#/">Каталог</a><a href="#/bookings">Бронирования</a><a href="/docs" target="_blank" rel="noopener">Документация API</a></div></div><div class="footer-bottom"><span>© ${new Date().getFullYear()} Набронировал. Pet-проект.</span><span>Создано на FastAPI + Docker + Nginx</span></div></div></footer>`;}
function layout(content) {app.innerHTML=navHTML()+`<main>${content}</main>`+footerHTML();}
function emptyHTML(title,desc,action='',error=false) {return `<div class="empty-state"><div class="empty-art">${ic(error?'alert':'suitcase')}</div><h3>${esc(title)}</h3><p>${esc(desc)}</p>${action}</div>`;}
function searchFormHTML(s){return `<div class="search-overlap"><form id="search-form" class="search-panel">
<div class="field"><label for="location">Куда отправимся?</label><div class="field-control">${ic('pin')}<input id="location" name="location" placeholder="Город или направление" value="${esc(s.location)}" autocomplete="off"></div></div>
<div class="field"><label for="date_from">Дата заезда</label><div class="field-control">${ic('calendar')}<input id="date_from" name="date_from" type="date" min="${today()}" value="${esc(s.date_from)}" required></div></div>
<div class="field"><label for="date_to">Дата выезда</label><div class="field-control">${ic('calendar')}<input id="date_to" name="date_to" type="date" min="${esc(shiftDays(s.date_from,1))}" value="${esc(s.date_to)}" required></div></div>
<button class="btn btn-primary search-submit" type="submit">${ic('search')} Найти жильё</button></form><p class="search-hint">${ic('info')}Поиск показывает отели, где есть свободные номера на указанные даты. Можно указать и название отеля в каталоге.</p></div>`;}
function homeHTML(s){return `<div class="wrap hero-wrap"><section class="hero"><div class="hero-scene" aria-hidden="true"></div><div class="hero-copy"><span class="hero-label"><i></i> Время новых впечатлений</span><h1>Уезжай за <em>впечатлениями.</em><br>Остальное — за нами.</h1><p>Планируй поездку по-своему: выбирай направление, сравнивай номера и бронируй в несколько кликов.</p><div class="hero-stat"><span>${ic('shield','icon-sm')} Без лишних шагов</span><span>${ic('calendar','icon-sm')} Поиск по датам</span></div></div></section>${searchFormHTML(s)}</div>
<div class="wrap"><section class="section" id="results"><div class="section-heading"><div><span class="eyebrow">ТВОЯ СЛЕДУЮЩАЯ ПОЕЗДКА</span><h2>Подходящие варианты</h2><p class="section-subheading">Результаты берём непосредственно из каталога бронирования</p></div><span class="pill">${ic('spark','icon-sm')} Актуально на выбранные даты</span></div>
<div class="catalog-tools"><div class="mini-filter"><button class="chip" type="button" data-city="">Все направления</button><button class="chip" type="button" data-city="Москва">Москва</button><button class="chip" type="button" data-city="Санкт-Петербург">Санкт-Петербург</button><button class="chip" type="button" data-city="Сочи">Сочи</button><button class="chip" type="button" data-city="Казань">Казань</button></div><form id="hotel-title-form" class="hotel-title-form"><input name="title" aria-label="Название отеля" placeholder="Поиск по названию" value="${esc(s.title)}"><button type="submit" title="Найти по названию">${ic('search','icon-sm')}</button></form></div>
<div id="catalog-status" class="results-note" style="margin-top:22px">${ic('clock','icon-sm')}Ищем свободные номера…</div><div id="hotel-grid" class="hotel-grid">${Array(6).fill('<div class="loading-card"></div>').join('')}</div><div id="catalog-more"></div></section>
<div class="benefits"><div class="benefit"><div class="benefit-icon">${ic('search')}</div><div><h4>Всё в одном поиске</h4><p>Указывай город и даты — показываем подходящие доступные варианты.</p></div></div><div class="benefit"><div class="benefit-icon">${ic('calendar')}</div><div><h4>Выбирай подходящие даты</h4><p>Смотри номера и стоимость проживания перед подтверждением брони.</p></div></div><div class="benefit"><div class="benefit-icon">${ic('lock')}</div><div><h4>Бронирования в профиле</h4><p>История твоих бронирований доступна после входа в аккаунт.</p></div></div></div></div>`;}
function hotelCardHTML(h,rooms,s){const img=roomImage(rooms?.find(r=>roomImage(r)));const min=rooms?.length?Math.min(...rooms.map(x=>Number(x.price)).filter(x=>Number.isFinite(x)&&x>0)):null;return `<article class="hotel-card"><a href="${detailHref(h.id,s)}" aria-label="Смотреть номера в ${esc(h.title)}"><div class="hotel-cover">${cover(img)}<span class="cover-badge">${ic('bed','icon-sm')} Отель</span></div></a><div class="hotel-card-body"><div class="hotel-meta">${ic('spark','icon-sm')} Доступно на выбранные даты</div><h3>${esc(h.title)}</h3><div class="hotel-location">${ic('pin','icon-sm')}<span>${esc(h.location)}</span></div><div class="hotel-card-footer"><div><div class="hotel-price-label">${min?'от / ночь':'Стоимость'}</div>${min?`<div class="hotel-price">${rub(min)} <small>/ ночь</small></div>`:`<div class="hotel-price-unknown">Смотреть номера</div>`}</div><a class="btn btn-soft btn-small" href="${detailHref(h.id,s)}">Подробнее ${ic('arrow','icon-sm')}</a></div></div></article>`;}
async function loadHotels(s,append=false) {
  const grid=document.querySelector('#hotel-grid'),status=document.querySelector('#catalog-status'),more=document.querySelector('#catalog-more');
  if(!grid||!status||state.searchPending)return;
  const requestToken=state.token;state.searchPending=true;
  if(!append){state.searchPage=1;state.searchResults=[];grid.innerHTML=Array(6).fill('<div class="loading-card"></div>').join('');}
  else {more.innerHTML=`<span class="inline-loader"><i class="spinner"></i> Загружаем…</span>`;}
  try {
    const query=routeSearchParams({...s,page:state.searchPage,per_page:state.perPage});
    const response=await request('/hotels?'+query);
    if(requestToken!==state.token)return;
    const hotels=Array.isArray(response?.data)?response.data:[];
    const enriched=await Promise.all(hotels.map(async h=>{
      try{const rooms=await request(`/hotels/${encodeURIComponent(h.id)}/rooms?${routeSearchParams({date_from:s.date_from,date_to:s.date_to})}`);return {hotel:h,rooms:Array.isArray(rooms)?rooms:[]};}
      catch{return {hotel:h,rooms:[]};}
    }));
    if(requestToken!==state.token)return;
    state.searchResults.push(...enriched);
    grid.innerHTML=state.searchResults.map(({hotel,rooms})=>hotelCardHTML(hotel,rooms,s)).join('')||emptyHTML('Пока нет свободных вариантов','Измени даты или попробуй другой город — поиск проверяет доступность, а не просто список всех отелей.','<button class="btn btn-primary" type="button" data-reset-search>Сбросить поиск</button>');
    status.innerHTML=ic('check','icon-sm')+`Показано отелей: ${state.searchResults.length}`;
    more.innerHTML=hotels.length===state.perPage?'<button class="btn btn-ghost load-more" type="button" data-more>Показать ещё</button>':'';
    state.searchPage++;
  }catch(e){if(requestToken!==state.token)return;grid.innerHTML=emptyHTML('Не удалось получить каталог',e.message,'<button class="btn btn-primary" type="button" data-retry>Повторить</button>',true);status.textContent='Ошибка загрузки';more.innerHTML='';}
  finally{if(requestToken===state.token)state.searchPending=false;}
}
function detailDates(search) {const d=searchDefaults();const from=search.date_from||d.date_from,to=search.date_to||d.date_to;return {date_from:from,date_to:to};}
function detailHTML(id,s){return `<div class="wrap subpage"><a href="#/search?${routeSearchParams(s)}" class="back-link">${ic('back','icon-sm')} К результатам поиска</a><div id="detail-content"><div class="detail-topline"><div><span class="eyebrow">ОТЕЛЬ И НОМЕРА</span><h1>Загружаем отель…</h1></div></div><div class="detail-visual" style="background:#dce9e3"></div><div class="inline-loader"><span class="spinner"></span>Проверяем доступность номеров</div></div></div>`;}
async function loadDetail(id,s){const token=state.token;const mount=document.querySelector('#detail-content');if(!mount)return;
try{const [h,r]=await Promise.all([request(`/hotels/${id}`),request(`/hotels/${id}/rooms?${routeSearchParams(s)}`)]);if(token!==state.token)return;
const hotel=h?.data||{};const rooms=Array.isArray(r)?r:[];const visual=roomImage(rooms.find(x=>roomImage(x)));
mount.innerHTML=`<div class="detail-topline"><div><span class="eyebrow">ОТЕЛЬ И НОМЕРА</span><h1>${esc(hotel.title||'Отель')}</h1><div class="detail-location">${ic('pin','icon-sm')}${esc(hotel.location||'')}</div></div><span class="pill">${ic('calendar','icon-sm')}${dateText(s.date_from)} — ${dateText(s.date_to)}</span></div>
<div class="detail-visual">${cover(visual)}<span class="visual-overlay"></span><span class="detail-pill">${ic('spark','icon-sm')} Выбирай свой номер</span></div>
<div class="rooms-heading"><div><span class="eyebrow">СВОБОДНЫЕ НОМЕРА</span><h2>Остановись с комфортом</h2><p>${nights(s.date_from,s.date_to)} ноч. · с ${dateText(s.date_from)} по ${dateText(s.date_to)}</p></div><a class="btn btn-ghost btn-small" href="#/">${ic('calendar','icon-sm')} Изменить даты</a></div>
${rooms.length?`<div class="rooms-stack">${rooms.map(room=>roomHTML(room,s)).join('')}</div>`:emptyHTML('На эти даты мест нет','Попробуй изменить период проживания или выбрать другой отель.','<a href="#/" class="btn btn-primary">Другие варианты</a>')}
<p class="note" style="margin-top:26px">${ic('info')}Бронирование создаётся через твой FastAPI. Оплата онлайн в текущем API не реализована.</p>`;
}catch(e){if(token!==state.token)return;mount.innerHTML=emptyHTML('Не удалось загрузить отель',e.message,'<a href="#/" class="btn btn-primary">К поиску</a>',true);}}
function roomHTML(r,s){const photo=roomImage(r),count=nights(s.date_from,s.date_to);return `<article class="room-card"><div class="room-cover">${cover(photo)}</div><div class="room-main"><h3>${esc(r.title)}</h3><p>${esc(r.description||'Уточни детали номера перед бронированием.')}</p><div class="amenities">${(r.facilities||[]).slice(0,7).map(f=>`<span class="amenity">${ic('check','icon-sm')} ${esc(f.title)}</span>`).join('')||'<span class="amenity">Информация об удобствах уточняется</span>'}</div></div><div class="room-price"><span>Цена за ночь</span><strong>${rub(r.price)}</strong><div class="total">За ${count} ноч.: <b>${rub(r.price*count)}</b></div><button class="btn btn-primary" type="button" data-book="${Number(r.id)}" data-room-title="${esc(r.title)}" data-room-price="${Number(r.price)}">Забронировать ${ic('arrow','icon-sm')}</button></div></article>`;}
function authHTML(mode){const register=mode==='register';return `<div class="wrap subpage"><div class="auth-layout"><div class="auth-visual"><div><span class="hero-label">${ic('spark','icon-sm')} БОЛЬШЕ ПУТЕШЕСТВИЙ</span><h2>Твои планы заслуживают красивого начала.</h2><p>Создай аккаунт, чтобы оформлять бронирования и видеть свои поездки в одном месте.</p></div><span style="color:#b2ccc2;font-size:12px">Набронировал · Сделано для путешествий</span></div><div class="auth-form"><span class="eyebrow">ЛИЧНЫЙ КАБИНЕТ</span><h1>${register?'Создать аккаунт':'С возвращением!'}</h1><p>${register?'Укажи почту и придумай пароль, чтобы начать.':'Войди, чтобы продолжить бронирование или посмотреть свои поездки.'}</p><form id="auth-form" data-mode="${mode}"><div class="field"><label for="email">Электронная почта</label><div class="field-control">${ic('mail')}<input id="email" name="email" type="email" placeholder="you@example.com" autocomplete="email" required></div></div><div class="field"><label for="password">Пароль</label><div class="field-control">${ic('lock')}<input id="password" name="password" type="password" placeholder="Введите пароль" autocomplete="${register?'new-password':'current-password'}" minlength="1" required></div></div><button class="btn btn-primary btn-full" type="submit">${register?'Зарегистрироваться':'Войти'} ${ic('arrow','icon-sm')}</button></form><div class="auth-bottom">${register?'Уже есть аккаунт? <a href="#/login">Войти</a>':'Нет аккаунта? <a href="#/register">Зарегистрироваться</a>'}</div></div></div></div>`;}
function bookingsHTML(){return `<div class="wrap subpage"><a href="#/" class="back-link">${ic('back','icon-sm')} На главную</a><div class="section-heading"><div><span class="eyebrow">ЛИЧНЫЙ КАБИНЕТ</span><h2>Мои бронирования</h2><p>Все твои брони, оформленные в этом аккаунте</p></div><a href="#/" class="btn btn-primary btn-small">Найти ещё жильё ${ic('arrow','icon-sm')}</a></div><div id="bookings-list"><div class="inline-loader"><span class="spinner"></span>Загружаем бронирования…</div></div></div>`;}
async function loadBookings(){const token=state.token;const list=document.querySelector('#bookings-list');if(!list)return;
try{const rows=await request('/bookings/me');if(token!==state.token)return;
if(!Array.isArray(rows)||rows.length===0){list.innerHTML=emptyHTML('Пока никаких бронирований','Когда выберешь и забронируешь номер, он появится здесь.','<a href="#/" class="btn btn-primary">Выбрать отель</a>');return;}
list.innerHTML=rows.slice().sort((a,b)=>b.id-a.id).map(b=>`<article class="booking-row"><div class="booking-icon">${ic('bed','icon-lg')}</div><div><h3>Бронирование №${esc(b.id)} · номер №${esc(b.room_id)}</h3><p>${ic('calendar','icon-sm')} Заезд: ${dateText(b.date_from)} · Выезд: ${dateText(b.date_to)} · ${nights(b.date_from,b.date_to)} ноч.</p><span class="status-tag">Бронь создана</span></div><div class="booking-total"><strong>${rub(b.price*nights(b.date_from,b.date_to))}</strong><span>${rub(b.price)} / ночь</span></div></article>`).join('')+`<p class="note" style="margin-top:22px">${ic('info')}Текущая ручка /bookings/me возвращает ID номера, даты и цену. Для названия отеля в списке нужен расширенный ответ бэкенда.</p>`;
}catch(e){if(token!==state.token)return;if(e.status===401){go('#/login');return;}list.innerHTML=emptyHTML('Не удалось получить бронирования',e.message,'<button class="btn btn-primary" type="button" data-retry-bookings>Повторить</button>',true);}}
async function checkAuth(){try{const response=await request('/auth/me');state.user=response?.user||null;}catch{state.user=null;}}
async function handleAuth(form){const button=form.querySelector('button[type="submit"]');const mode=form.dataset.mode;const payload={email:form.elements.namedItem('email').value.trim(),password:form.elements.namedItem('password').value};button.disabled=true;button.textContent='Проверяем данные…';
try{if(mode==='register')await request('/auth/register',{method:'POST',body:JSON.stringify(payload)});await request('/auth/login',{method:'POST',body:JSON.stringify(payload)});await checkAuth();toast(mode==='register'?'Аккаунт создан. Добро пожаловать!':'Успешный вход');const next=state.afterLogin;state.afterLogin=null;go(next||'#/bookings');}
catch(e){toast(e.message,true);button.disabled=false;button.innerHTML=`${mode==='register'?'Зарегистрироваться':'Войти'} ${ic('arrow','icon-sm')}`;}}
async function handleLogout(){try{await request('/auth/logout',{method:'POST'});state.user=null;toast('Ты вышел из аккаунта');go('#/');}catch(e){toast(e.message,true);}}
function startBooking(roomId,title,price){const s=state.search||searchDefaults();if(!state.user){state.afterLogin=location.hash||'#/';toast('Чтобы забронировать номер, сначала войди в аккаунт');go('#/login');return;}
const count=nights(s.date_from,s.date_to);if(count<1){toast('Укажи корректные даты',true);return;}
dialog.innerHTML=`<span class="eyebrow">ПОДТВЕРЖДЕНИЕ</span><h3 id="confirm-title">Почти готово!</h3><p>Проверь даты и номер. После подтверждения бронирование появится в твоём личном кабинете.</p><div class="confirm-detail"><span class="muted">${esc(title)}</span><strong>${rub(price*count)}</strong><span class="muted">${dateText(s.date_from)} — ${dateText(s.date_to)} · ${count} ноч.</span></div><div class="dialog-actions"><button class="btn btn-ghost" type="button" data-cancel-book>Отмена</button><button class="btn btn-primary" type="button" data-confirm-book="${Number(roomId)}">Подтвердить</button></div>`;
dialog.showModal();}
async function confirmBooking(roomId,button){button.disabled=true;button.textContent='Бронируем…';const s=state.search||searchDefaults();try{await request('/bookings',{method:'POST',body:JSON.stringify({room_id:roomId,date_from:s.date_from,date_to:s.date_to})});dialog.close();toast('Готово! Бронирование оформлено');go('#/bookings');}catch(e){toast(e.message,true);button.disabled=false;button.textContent='Подтвердить';}}
function render(){state.token++;state.searchPending=false;const {path,query}=parseRoute();window.scrollTo({top:0,behavior:'instant'});
if(path==='/'||path==='/search'){
const defaults=searchDefaults();const s={location:query.get('location')||'',title:query.get('title')||'',date_from:query.get('date_from')||defaults.date_from,date_to:query.get('date_to')||defaults.date_to};state.search=s;layout(homeHTML(s));if(nights(s.date_from,s.date_to)<1){document.querySelector('#hotel-grid').innerHTML=emptyHTML('Исправь даты','Выезд должен быть позже заезда.');return;}loadHotels(s);return;}
const match=path.match(/^\/hotel\/(\d+)$/);if(match){const s=detailDates(Object.fromEntries(query.entries()));state.search=s;layout(detailHTML(match[1],s));if(nights(s.date_from,s.date_to)<1){document.querySelector('#detail-content').innerHTML=emptyHTML('Некорректные даты','Выезд должен быть позже заезда.');return;}loadDetail(match[1],s);return;}
if(path==='/login'||path==='/register'){if(state.user){go('#/bookings');return;}layout(authHTML(path.slice(1)));return;}
if(path==='/bookings'){if(!state.user){state.afterLogin='#/bookings';go('#/login');return;}layout(bookingsHTML());loadBookings();return;}
layout(`<div class="wrap subpage">${emptyHTML('Страница не найдена','Попробуй перейти на главную.','<a href="#/" class="btn btn-primary">На главную</a>')}</div>`);}

document.addEventListener('submit',e=>{const form=e.target;if(form.id==='search-form'){e.preventDefault();const data=Object.fromEntries(new FormData(form).entries());if(nights(data.date_from,data.date_to)<1){toast('Дата выезда должна быть позже даты заезда',true);return;}go('#/search?'+routeSearchParams(data));}
if(form.id==='auth-form'){e.preventDefault();handleAuth(form);}
if(form.id==='hotel-title-form'){e.preventDefault();const title=form.elements.namedItem('title').value.trim();go('#/search?'+routeSearchParams({...state.search,title}));}});
document.addEventListener('change',e=>{if(e.target.id==='date_from'){const end=document.querySelector('#date_to');if(end){end.min=shiftDays(e.target.value,1);if(end.value<=e.target.value)end.value=shiftDays(e.target.value,1);}}});
document.addEventListener('click',e=>{const more=e.target.closest('[data-more]');if(more){loadHotels(state.search,true);return;}
const city=e.target.closest('[data-city]');if(city){const search={...(state.search||searchDefaults()),location:city.dataset.city};go('#/search?'+routeSearchParams(search));return;}
if(e.target.closest('[data-reset-search]')){go('#/search?'+routeSearchParams(searchDefaults()));return;}
if(e.target.closest('[data-retry]')){loadHotels(state.search);return;}
if(e.target.closest('[data-retry-bookings]')){loadBookings();return;}
if(e.target.closest('[data-logout]')){handleLogout();return;}
const book=e.target.closest('[data-book]');if(book){startBooking(Number(book.dataset.book),book.dataset.roomTitle,Number(book.dataset.roomPrice));return;}
if(e.target.closest('[data-cancel-book]')){dialog.close();return;}
const confirm=e.target.closest('[data-confirm-book]');if(confirm){confirmBooking(Number(confirm.dataset.confirmBook),confirm);return;}});
// Некорректное / отсутствующее изображение не должно портить страницу.
document.addEventListener('error',e=>{const el=e.target;if(el instanceof HTMLImageElement && el.hasAttribute('data-image-fallback')){el.removeAttribute('data-image-fallback');el.src='/assets/placeholder.svg';}},true);
window.addEventListener('hashchange',render);
(async()=>{await checkAuth();render();})();
