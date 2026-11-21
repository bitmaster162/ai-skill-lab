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
    allowed: 'Enabled', denied: 'Off', signal: 'Your browser privacy signal is active.'
  } : {
    heading: 'Статистика посещений по желанию',
    details: 'Если вам уже есть 18 лет, вы можете разрешить Google Аналитике учитывать посещения страниц для взрослых и бизнеса с помощью аналитических cookies. Здесь можно изменить свой выбор.',
    allow: 'Мне есть 18, разрешаю', decline: 'Отклонить', withdraw: 'Отозвать согласие',
    allowed: 'Включена', denied: 'Выключена', signal: 'Ваш браузер передал сигнал отказа от отслеживания.'
  };
  const id = 'G-6RY1HZ75FD';
  const key = 'aisl.adult-analytics.v1';
  const allow = document.getElementById('allow');
  const decline = document.getElementById('decline');
  const state = document.getElementById('state');
  const privacySignal = () => navigator.globalPrivacyControl === true || navigator.doNotTrack === '1';
  function savedChoice() {
    try {
      const value = localStorage.getItem(key);
      // Do not reuse an old opt-in if the browser can no longer save a withdrawal.
      if (value === 'allow') localStorage.setItem(key, value);
      return value;
    } catch { return 'deny'; }
  }
  let choice = location.hash === '#off' ? 'deny' : savedChoice();
  let started = false;
  document.documentElement.lang = english ? 'en' : 'ru';
  document.getElementById('heading').textContent = copy.heading;
  document.getElementById('details').textContent = copy.details;
  allow.textContent = copy.allow;

  function render() {
    allow.disabled = privacySignal() || choice === 'allow';
    decline.textContent = !privacySignal() && choice === 'allow' ? copy.withdraw : copy.decline;
    state.textContent = privacySignal() ? copy.signal : choice === 'allow' ? copy.allowed : choice === 'deny' ? copy.denied : '';
    document.querySelector('section').hidden = false;
  }
  function forgetCookies() {
    for (const item of document.cookie.split(';')) {
      const name = item.trim().split('=')[0];
      if (/^aisl_ga(?:_|$)/.test(name)) {
        document.cookie = name + '=; Max-Age=0; Path=/analytics/; Secure; SameSite=Lax';
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
    const context = {
      page_location: 'https://aiskillab.work' + page,
      page_title: pages.get(page), page_referrer: searchOrigin()
    };
    gtag('consent', 'default', {
      analytics_storage: 'granted', ad_storage: 'denied',
      ad_user_data: 'denied', ad_personalization: 'denied'
    });
    gtag('set', context);
    gtag('js', new Date());
    gtag('config', id, {
      ...context, send_page_view: false, allow_google_signals: false,
      allow_ad_personalization_signals: false, cookie_domain: 'none',
      cookie_path: '/analytics/', cookie_prefix: 'aisl', cookie_expires: 60 * 60 * 24 * 30
    });
    gtag('event', 'page_view', { ...context, send_to: id });
    const script = document.createElement('script');
    script.async = true;
    script.referrerPolicy = 'no-referrer';
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.appendChild(script);
  }
  function apply(value, persist) {
    choice = value;
    if (persist) {
      try {
        if (value === 'deny') localStorage.removeItem(key);
        localStorage.setItem(key, value);
      } catch { choice = 'deny'; }
    }
    if (choice === 'allow' && !privacySignal()) count();
    else {
      window['ga-disable-' + id] = true;
      forgetCookies();
      if (started) {
        // Preserve denial through reload even if storage writes have been blocked.
        history.replaceState(null, '', location.pathname + '#off');
        location.reload();
        return;
      }
    }
    render();
  }
  allow.addEventListener('click', () => { if (!privacySignal()) apply('allow', true); });
  decline.addEventListener('click', () => apply('deny', true));
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) apply(event.newValue === 'allow' ? 'allow' : 'deny', false);
  });
  // Freeze the loaded tag before navigation. A cached page must recheck the
  // browser's current choice before the existing document can resume.
  window.addEventListener('pagehide', () => { window['ga-disable-' + id] = true; });
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    const current = location.hash === '#off' ? 'deny' : savedChoice();
    window['ga-disable-' + id] = current !== 'allow' || privacySignal();
    apply(current, false);
  });
  apply(choice, false);
})();
