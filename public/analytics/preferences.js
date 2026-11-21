// Dedicated document: its tag and timers are discarded when an adult page is left.
(() => {
  'use strict';
  if (window === window.parent || window.location.origin !== 'https://aiskillab.work') return;
  const pages = new Map([
    ['/business', 'AI для бизнеса'], ['/en/business', 'AI for business'],
    ['/personal', 'AI для взрослых'], ['/en/personal', 'AI for adults']
  ]);
  let page;
  try {
    if (parent.location.origin !== location.origin) return;
    page = parent.location.pathname.replace(/\/$/, '');
  } catch { return; }
  if (!pages.has(page)) return;
  const english = page.startsWith('/en/');
  const copy = english ? {
    heading: 'Optional audience measurement',
    details: 'If you are 18 or older, you can allow Google Analytics to count visits to our adult and business pages using analytics cookies. You can change your choice here.',
    allow: 'I am 18+ and allow', decline: 'Decline', withdraw: 'Withdraw consent',
    allowed: 'Enabled', denied: 'Off', signal: 'Your browser privacy signal is active.',
    unsaved: 'Off on this page. Your browser blocked both ways of saving withdrawal. Clear the site data to remove the previous choice.'
  } : {
    heading: 'Статистика посещений по желанию',
    details: 'Если вам уже есть 18 лет, вы можете разрешить Google Аналитике учитывать посещения страниц для взрослых и бизнеса с помощью аналитических cookies. Здесь можно изменить свой выбор.',
    allow: 'Мне есть 18, разрешаю', decline: 'Отклонить', withdraw: 'Отозвать согласие',
    allowed: 'Включена', denied: 'Выключена', signal: 'Ваш браузер передал сигнал отказа от отслеживания.',
    unsaved: 'На этой странице статистика выключена. Браузер заблокировал сохранение отказа. Очистите данные сайта, чтобы удалить прежний выбор.'
  };
  const id = 'G-6RY1HZ75FD';
  const key = 'aisl.adult-analytics.v1';
  const allow = document.getElementById('allow');
  const decline = document.getElementById('decline');
  const state = document.getElementById('state');
  const privacySignal = () => navigator.globalPrivacyControl === true || navigator.doNotTrack === '1';
  const grantCookie = 'aisl_consent_grant';
  const cookieScope = '; Path=/analytics/; Secure; SameSite=Strict';
  const thirtyDays = 30 * 24 * 60 * 60;
  const revokedHere = () => location.hash === '#off' || location.hash === '#off-storage';
  let unsaved = location.hash === '#off-storage';

  function hasGrantCookie() {
    return document.cookie.split(';').some(part => part.trim() === grantCookie + '=1');
  }
  function savedChoice() {
    try {
      const value = localStorage.getItem(key);
      if (value !== 'allow') return value;
      // Reusing consent requires two independent, unexpired affirmative records.
      if (!hasGrantCookie()) return 'deny';
      localStorage.setItem(key, value);
      return 'allow';
    } catch { return 'deny'; }
  }
  function saveChoice(value) {
    unsaved = false;
    if (value === 'allow') {
      try {
        document.cookie = grantCookie + '=1; Max-Age=' + thirtyDays + cookieScope;
        localStorage.setItem(key, 'allow');
        return savedChoice() === 'allow' ? 'allow' : 'deny';
      } catch { return 'deny'; }
    }
    // Clearing either record prevents a stale grant from reviving on a new document.
    let storageRevoked = false;
    let cookieRevoked = false;
    try {
      localStorage.removeItem(key);
      storageRevoked = localStorage.getItem(key) !== 'allow';
      localStorage.setItem(key, 'deny');
    } catch { /* The scoped first-party consent cookie provides the second path. */ }
    try {
      if (storageRevoked) {
        if (hasGrantCookie()) document.cookie = grantCookie + '=; Max-Age=0' + cookieScope;
      } else {
        // Verify an explicit veto. An empty cookie string could mean reads are blocked.
        document.cookie = grantCookie + '=0; Max-Age=' + thirtyDays + cookieScope;
        cookieRevoked = document.cookie.split(';').some(part => part.trim() === grantCookie + '=0');
      }
    } catch { /* A successful localStorage revocation is sufficient. */ }
    unsaved = !storageRevoked && !cookieRevoked;
    return 'deny';
  }
  let choice = revokedHere() ? 'deny' : savedChoice();
  let started = false;
  document.documentElement.lang = english ? 'en' : 'ru';
  document.getElementById('heading').textContent = copy.heading;
  document.getElementById('details').textContent = copy.details;
  allow.textContent = copy.allow;

  function render() {
    allow.disabled = privacySignal() || choice === 'allow';
    decline.textContent = !privacySignal() && choice === 'allow' ? copy.withdraw : copy.decline;
    state.textContent = unsaved ? copy.unsaved : privacySignal() ? copy.signal : choice === 'allow' ? copy.allowed : choice === 'deny' ? copy.denied : '';
    document.querySelector('section').hidden = false;
  }
  function forgetCookies() {
    let cookies;
    try { cookies = document.cookie; } catch { return; }
    for (const item of cookies.split(';')) {
      const name = item.trim().split('=')[0];
      if (/^aisl_ga(?:_|$)/.test(name)) {
        try { document.cookie = name + '=; Max-Age=0; Path=/analytics/; Secure; SameSite=Lax'; }
        catch { /* Disabled analytics must still unload when cookie writes are blocked. */ }
      }
    }
  }
  function searchOrigin() {
    // Only explicitly listed search origins are meaningful to traffic acquisition.
    // Discard paths, search terms, credentials, ports, and every other referrer.
    const searchHosts = ['www.google.com', 'www.google.ru', 'www.google.co.th',
      'www.bing.com', 'search.yahoo.com', 'duckduckgo.com', 'yandex.ru', 'ya.ru'];
    try {
      const ref = new URL(parent.document.referrer);
      if (ref.protocol === 'https:' && !ref.port && !ref.username && !ref.password &&
          searchHosts.includes(ref.hostname)) return 'https://' + ref.hostname + '/';
    } catch { /* Direct or inaccessible referrer. */ }
    return '';
  }
  function count() {
    if (started || privacySignal() || choice !== 'allow' || !pages.has(page)) return;
    started = true;
    window['ga-disable-' + id] = false;
    const gtag = function () { (window.dataLayer ||= []).push(arguments); };
    // Keep the actual document URL, parent referrer and all form/input text out of GA.
    const settings = {
      page_location: 'https://aiskillab.work' + page,
      page_title: pages.get(page), page_referrer: searchOrigin(),
      allow_google_signals: false, allow_ad_personalization_signals: false,
      cookie_domain: 'none', cookie_path: '/analytics/', cookie_prefix: 'aisl',
      cookie_expires: thirtyDays, cookie_update: false
    };
    gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied',
      ad_user_data: 'denied', ad_personalization: 'denied'
    });
    // The SDK initializes cookies from global settings. Set them before js/config.
    gtag('set', settings);
    gtag('js', new Date());
    // Configure exactly one automatic page view for this document.
    gtag('config', id, { ...settings, send_page_view: true });
    const script = document.createElement('script');
    script.async = true;
    script.referrerPolicy = 'no-referrer';
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(script);
  }
  let channel;
  try { channel = new BroadcastChannel(key); } catch { /* Optional cross-tab delivery. */ }
  function apply(value, persist) {
    choice = persist ? saveChoice(value) : value;
    if (persist && choice === 'allow' && revokedHere()) {
      history.replaceState(null, '', location.pathname);
    }
    if (persist && value === 'deny') channel?.postMessage('deny');
    if (choice === 'allow' && !privacySignal()) count();
    else {
      window['ga-disable-' + id] = true;
      forgetCookies();
      if (started) {
        // Preserve denial through reload even if storage writes have been blocked.
        history.replaceState(null, '', location.pathname + (unsaved ? '#off-storage' : '#off'));
        location.reload();
        return;
      }
    }
    render();
  }
  allow.addEventListener('click', () => { if (!privacySignal()) apply('allow', true); });
  decline.addEventListener('click', () => apply('deny', true));
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) apply(event.newValue === 'allow' ? savedChoice() : 'deny', false);
  });
  if (channel) channel.onmessage = event => {
    if (event.data === 'deny') apply('deny', false);
  };
  // Freeze the loaded tag before navigation. A cached page must recheck the
  // browser's current choice before the existing document can resume.
  window.addEventListener('pagehide', () => { window['ga-disable-' + id] = true; });
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    const current = revokedHere() ? 'deny' : savedChoice();
    window['ga-disable-' + id] = current !== 'allow' || privacySignal();
    apply(current, false);
  });
  apply(choice, false);
})();
