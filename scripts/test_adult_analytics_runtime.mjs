import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('../deploy/live/analytics/preferences.js', import.meta.url), 'utf8');
const origin = 'https://aiskillab.work';
const key = 'aisl.adult-analytics.v1';
const id = 'G-6RY1HZ75FD';

function fixture({ path = '/en/business', prior, gpc = false, dnt = '0', originOverride = origin,
  top = false, referrer = 'https://www.google.com/search?q=private-contact', readOnly = false,
  savedValues, savedCookies, hash = '' } = {}) {
  const nodes = new Map();
  const handlers = {};
  const scripts = [];
  const writes = [];
  const values = savedValues || new Map(prior ? [[key, prior]] : []);
  const cookies = savedCookies || new Map([['unrelated','keep'], ['aisl_ga','client']]);
  if (prior === 'allow' && !savedCookies) cookies.set('aisl_consent_grant', '1');
  const blocked = { storage: readOnly, cookies: false };
  const messages = [];
  class BroadcastChannel {
    constructor() { messages.push(this); }
    postMessage(value) { this.sent = value; }
  }
  const element = name => {
    if (!nodes.has(name)) nodes.set(name, { hidden: true, addEventListener(type, listener) { this[type] = listener; } });
    return nodes.get(name);
  };
  let reloaded = 0;
  const loc = { origin: originOverride, pathname: '/analytics/preferences.htm', search: '', hash,
    reload() { reloaded++; } };
  const document = {
    documentElement: {}, head: { appendChild(script) { scripts.push(script); } },
    getElementById: element, querySelector: element, createElement() { return {}; },
    get cookie() { return [...cookies].map(([name,value]) => name + '=' + value).join('; '); },
    set cookie(value) {
      if (blocked.cookies) return;
      writes.push(value);
      const [name, data] = value.split(';')[0].split('=');
      if (value.includes('Max-Age=0;')) cookies.delete(name);
      else cookies.set(name, data);
    },
  };
  const parent = { location: { origin, pathname: path, search: '?email=raw-canary', hash: '#secret-fragment' },
    document: { referrer, title: 'Private browser title', cookie: 'private-credential' } };
  const window = { location: loc, parent, addEventListener(type, cb) { handlers[type] = cb; } };
  if (top) window.parent = window;
  const navigator = { globalPrivacyControl: gpc, doNotTrack: dnt };
  const localStorage = { getItem(k) { return values.get(k) ?? null; },
    setItem(k, v) { if (blocked.storage) throw Error('read-only'); values.set(k, v); },
    removeItem(k) { if (blocked.storage) throw Error('read-only'); values.delete(k); } };
  const history = { replaceState(_state, _title, url) { loc.hash = new URL(url, origin).hash; } };
  vm.runInNewContext(source, { window, parent: window.parent, document, location: loc, URL, navigator, localStorage, history, BroadcastChannel });
  return { window, navigator, scripts, nodes, handlers, values, writes, cookies, blocked, messages, reloaded: () => reloaded,
    events: () => Array.from(window.dataLayer || [], args => Array.from(args)) };
}

test('a fresh visitor, refusal and privacy signals never initialize Google', () => {
  for (const settings of [{}, {prior:'deny'}, {prior:'allow', gpc:true}, {prior:'allow', dnt:'1'}, {prior:'allow', readOnly:true}]) {
    const f = fixture(settings);
    assert.equal(f.scripts.length, 0);
    assert.deepEqual(f.events(), []);
    f.nodes.get('decline').click();
    assert.equal(f.scripts.length, 0);
    if (settings.gpc || settings.dnt || settings.readOnly) {
      f.nodes.get('allow').click();
      assert.equal(f.scripts.length, 0);
    }
  }
});

test('four adult routes send one explicitly sanitized pageview per document', () => {
  for (const path of ['/personal', '/business', '/en/personal', '/en/business']) {
    const f = fixture({path});
    f.nodes.get('allow').click();
    f.nodes.get('allow').click();
    assert.equal(f.values.get(key), 'allow');
    assert.equal(f.scripts.length, 1);
    assert.equal(f.scripts[0].referrerPolicy, 'no-referrer');
    assert.equal(f.scripts[0].src, 'https://www.googletagmanager.com/gtag/js?id=' + id);
    const events = f.events();
    assert.deepEqual(events.map(e => e[0]), ['consent', 'set', 'js', 'config']);
    const global = events[1][1];
    const config = events[3][2];
    assert.equal(events[3][1], id);
    assert.equal(config.send_page_view, true);
    assert.equal(global.allow_google_signals, false);
    assert.equal(global.allow_ad_personalization_signals, false);
    assert.equal(global.cookie_prefix, 'aisl');
    assert.equal(global.cookie_domain, 'none');
    assert.equal(global.cookie_path, '/analytics/');
    assert.equal(global.cookie_expires, 2592000);
    assert.equal(global.cookie_update, false);
    for (const [name,value] of Object.entries(global)) assert.equal(config[name], value);
    assert.equal(global.page_location, origin + path);
    assert.equal(global.page_referrer, 'https://www.google.com/');
    assert.doesNotMatch(JSON.stringify(events), /private-contact|raw-canary|secret-fragment|Private browser|private-credential/);
    assert.equal(f.nodes.get('allow').disabled, true);
  }
});

test('direct access, alternate hosts and excluded pages ignore a stored opt-in', () => {
  for (const opts of [{top:true}, {originOverride:'https://preview.example'},
    ...['/', '/en/teens', '/safety', '/en/start', '/matcher', '/en/business/child'].map(path => ({path}))]) {
    const f = fixture({prior:'allow', ...opts});
    assert.equal(f.scripts.length, 0); assert.deepEqual(f.events(), []);
  }
  for (const referrer of ['https://internal.example/secret', 'https://www.google.com.evil.example/secret',
    'https://private@www.google.com/', 'https://www.google.com:8443/secret', '', 'javascript:ignored']) {
    const f = fixture({prior:'allow', referrer});
    assert.equal(f.events().find(e => e[0] === 'config')[2].page_referrer, '');
  }
});

test('withdrawal unloads the tag and clears only scoped analytics cookies', () => {
  const f = fixture({prior:'allow'});
  f.nodes.get('decline').click();
  assert.equal(f.values.get(key), 'deny'); assert.equal(f.reloaded(),1);
  assert.equal(f.window['ga-disable-' + id], true);
  assert.equal(f.window.location.hash, '#off');
  assert(f.writes.some(write => /^aisl_ga=; Max-Age=0; Path=\/analytics\//.test(write)));
  assert.equal(f.cookies.has('aisl_consent_grant'), false);
  assert.equal(f.cookies.get('unrelated'), 'keep');
  const other = fixture({prior:'allow'});
  other.handlers.storage({key, newValue:'deny'});
  assert.equal(other.reloaded(),1); assert.equal(other.window['ga-disable-' + id],true);
});

test('a cached document rechecks consent and privacy signals without a duplicate event', () => {
  for (const change of ['none','revoke','signal']) {
    const f=fixture({prior:'allow'});
    f.handlers.pagehide({persisted:true});
    assert.equal(f.window['ga-disable-' + id], true);
    if (change === 'revoke') f.values.set(key,'deny');
    if (change === 'signal') f.navigator.globalPrivacyControl=true;
    f.handlers.pageshow({persisted:true});
    assert.equal(f.window['ga-disable-' + id], change !== 'none');
    assert.equal(f.reloaded(), change === 'none' ? 0 : 1);
    assert.equal(f.scripts.length,1); assert.equal(f.events().filter(e => e[0] === 'config').length,1);
  }
});

test('revocation survives failure of either store, navigation and storage recovery', () => {
  for (const store of ['storage', 'cookies']) {
    const current = fixture({prior:'allow'});
    assert.equal(current.scripts.length, 1);
    current.blocked[store] = true;
    current.nodes.get('decline').click();
    assert.equal(current.reloaded(), 1);
    assert.equal(current.messages[0].sent, 'deny');
    const revisit = fixture({savedValues:current.values, savedCookies:current.cookies});
    assert.equal(revisit.scripts.length, 0);
    assert.deepEqual(revisit.events(), []);
    assert.equal(revisit.nodes.get('state').textContent, 'Off');
    revisit.nodes.get('allow').click();
    assert.equal(revisit.scripts.length, 1);
    assert.equal(revisit.cookies.get('aisl_consent_grant'), '1');
  }
  const otherTab = fixture({prior:'allow'});
  otherTab.messages[0].onmessage({data:'deny'});
  assert.equal(otherTab.reloaded(), 1);
  assert.equal(otherTab.window['ga-disable-' + id], true);
});

test('blocked persistence is disclosed when neither store can record withdrawal', () => {
  const f = fixture({prior:'allow'});
  f.blocked.cookies = f.blocked.storage = true;
  f.nodes.get('decline').click();
  assert.equal(f.reloaded(),1);
  assert.equal(f.window.location.hash, '#off-storage');
  const reloaded = fixture({hash:'#off-storage', savedValues:f.values, savedCookies:f.cookies});
  assert.equal(reloaded.scripts.length, 0);
  assert.match(reloaded.nodes.get('state').textContent, /Clear the site data/);
});
