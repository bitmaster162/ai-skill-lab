// Offline behavioral contract for the separate R3 form runtime. No real network.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = fs.readFileSync(path.join(root, 'deploy/live/lead-form-runtime.js'), 'utf8');
assert.equal(source, fs.readFileSync(path.join(root, 'public/lead-form-runtime.js'), 'utf8'));
let checks = 1;
let cases = 0;
const eq = (a, b, message) => { checks++; assert.deepEqual(a, b, message); };
class Element {
  constructor(value = '') { this.value = value; this.checked = false; this.required = false; this.hidden = false; this.disabled = false; this.textContent = ''; this.className = ''; this.handlers = new Map(); }
  addEventListener(type, fn) { const a = this.handlers.get(type) || []; a.push(fn); this.handlers.set(type, a); }
  async trigger(type) { for (const fn of this.handlers.get(type) || []) await fn({ preventDefault() {} }); }
}
function fixture({ locale = 'en', audience = 'adult', response = 'ok', missing = '', fault = false, defer = false } = {}) {
  const audienceNode = new Element(audience);
  const submit = new Element(); submit.disabled = true;
  const readiness = new Element();
  const direct = new Element();
  const message = new Element();
  const success = new Element(); success.hidden = true;
  const adult = new Element();
  const adultWrap = new Element();
  const privacy = new Element(); privacy.checked = true;
  const form = new Element(); form.dataset = { leadState: 'unready' }; form.attributes = {};
  form.elements = { namedItem: (name) => name === 'audience' ? audienceNode : null };
  const values = { name: 'Synthetic Adult', contact: 'synthetic@example.invalid', goal: 'Offline validation only', locale, program: '', sourcePath: locale === 'en' ? '/en/start' : '/start', website: '' };
  const selectors = new Map([
    ['button[type="submit"]', submit], ['[data-lead-readiness]', readiness],
    ['[data-lead-direct-contact] a', direct], ['[data-lead-message]', message],
    ['[data-lead-success-actions]', success], ['[data-adult-confirmation]', adultWrap],
    ['input[name="adultConfirmation"]', adult],
  ]);
  form.querySelector = (s) => missing === s ? null : selectors.get(s) || null;
  form.setAttribute = (k, v) => { form.attributes[k] = v; if (k === 'data-lead-state') form.dataset.leadState = v; };
  form.checkValidity = () => privacy.checked && (!adult.required || adult.checked) && Boolean(values.name && values.contact && values.goal);
  form.reset = () => { audienceNode.value = 'adult'; adult.checked = false; privacy.checked = false; values.name = ''; values.contact = ''; values.goal = ''; };
  if (fault) audienceNode.addEventListener = () => { throw new Error('synthetic initialization fault'); };
  class FormDataMock {
    constructor(f) { assert.equal(f, form); }
    *entries() { yield* Object.entries({ ...values, audience: audienceNode.value }); if (privacy.checked) yield ['privacyConsent', 'yes']; if (adult.checked) yield ['adultConfirmation', 'yes']; }
  }
  const posts = [];
  const events = [];
  let release;
  const fetch = async (url, init) => {
    posts.push({ url, init });
    if (defer) await new Promise((resolve) => { release = resolve; });
    if (response === 'network') throw new Error('synthetic network error');
    return { ok: response !== 'http', async json() {
      if (response === 'json') throw new Error('synthetic malformed JSON');
      if (response === 'null') return null;
      return { ok: response === 'false' ? false : response === 'string' ? 'yes' : true, requestId: 'offline-fixture' };
    } };
  };
  class CustomEvent { constructor(type, init) { this.type = type; this.detail = init.detail; } }
  const context = vm.createContext({
    document: { documentElement: { lang: locale }, querySelector: (s) => s === 'form#application-form' ? form : null },
    fetch: missing === 'fetch' ? undefined : fetch,
    FormData: missing === 'FormData' ? undefined : FormDataMock,
    CustomEvent, dispatchEvent: (e) => { events.push({ type: e.type, detail: { ...e.detail } }); return true; }, console,
  });
  vm.runInContext('window = globalThis;', context);
  if (missing === 'fromEntries') vm.runInContext('Object.fromEntries = undefined;', context);
  const load = () => vm.runInContext(source, context, { filename: 'lead-form-runtime.js', timeout: 1000 });
  load(); cases++;
  eq(posts.length, 0, 'never fetch during initialization');
  return { form, submit, readiness, direct, message, success, audienceNode, adult, adultWrap, privacy, values, posts, events, load, release: () => release(), send: () => form.trigger('submit') };
}
for (const locale of ['ru', 'en']) {
  for (const audience of ['adult', 'parent', 'teen']) {
    const f = fixture({ locale, audience });
    eq(f.form.dataset.leadState, 'ready', 'handler initialized');
    eq(f.submit.disabled, false, 'button enabled last');
    eq(f.readiness.hidden, true, 'unavailable guidance hidden only when ready');
    eq(f.direct.hidden, false, 'direct contact remains accessible');
    eq(f.adult.required, audience !== 'adult', 'adult consent requirement');
    eq(f.adultWrap.hidden, audience === 'adult', 'adult consent visibility');
    if (audience !== 'adult') { await f.send(); eq(f.posts.length, 0, 'reject missing adult confirmation'); f.adult.checked = true; }
    await f.send();
    eq(f.posts.length, 1, 'one request');
    eq(f.posts[0].url, '/api/lead', 'same-origin lead route');
    eq(f.posts[0].init.method, 'POST', 'request method');
    eq(f.posts[0].init.headers['Content-Type'], 'application/json', 'request type');
    const data = JSON.parse(f.posts[0].init.body);
    eq(data.locale, locale, 'locale retained'); eq(data.audience, audience, 'audience retained');
    eq(data.sourcePath, locale === 'en' ? '/en/start' : '/start', 'source path');
    eq(data.privacyConsent, 'yes', 'privacy consent');
    eq(data.adultConfirmation, audience === 'adult' ? undefined : 'yes', 'adult confirmation payload');
    eq(f.message.textContent, locale === 'en' ? 'Application sent. We reply within 1–2 business days.' : 'Заявка отправлена. Ответим в течение 1–2 рабочих дней.', 'localized success');
    eq(f.success.hidden, false, 'continuation visible');
    eq(f.events, [{ type: 'asl:lead-event', detail: { event: 'lead_submit_ok' } }], 'one privacy-safe success event');
    eq(f.submit.disabled, false, 'not locked after completion');
    eq(f.form.attributes['aria-busy'], 'false', 'aria busy reset');
  }
  for (const response of ['http', 'false', 'string', 'null', 'json', 'network']) {
    const f = fixture({ locale, response }); const before = { ...f.values };
    await f.send();
    eq(f.posts.length, 1, 'failure attempt count');
    eq(f.values, before, 'error keeps user input');
    eq(f.message.className, 'formMessage error', 'error feedback');
    eq(f.success.hidden, true, 'no false continuation');
    eq(f.submit.disabled, false, 'retry is available after explicit user action');
    eq(f.events, [{ type: 'asl:lead-event', detail: { event: 'lead_submit_error' } }], 'one error event');
  }
  for (const missing of ['fetch', 'FormData', 'fromEntries', '[data-lead-readiness]', '[data-lead-direct-contact] a']) {
    const f = fixture({ locale, missing }); await f.send();
    eq(f.submit.disabled, true, 'missing capability or critical element leaves button disabled');
    eq(f.readiness.hidden, false, 'unavailable guidance not suppressed');
    eq(f.posts.length, 0, 'no request in failure mode');
  }
  const initFault = fixture({ locale, fault: true }); await initFault.send();
  eq(initFault.form.dataset.leadState, 'unready', 'partial init fails closed');
  eq(initFault.submit.disabled, true, 'partial init button'); eq(initFault.posts.length, 0, 'partial init no request');
  const privacy = fixture({ locale }); privacy.privacy.checked = false; await privacy.send();
  eq(privacy.posts.length, 0, 'privacy consent is mandatory');
  const twice = fixture({ locale }); twice.load();
  eq(twice.form.handlers.get('submit').length, 1, 'second script load adds no listener');
  await twice.send(); eq(twice.posts.length, 1, 'second script load no duplicate request');
  const busy = fixture({ locale, defer: true }); const pending = busy.send();
  eq(busy.submit.disabled, true, 'pending disables button'); eq(busy.form.attributes['aria-busy'], 'true', 'pending aria-busy');
  await busy.send(); eq(busy.posts.length, 1, 'double submit prevented');
  busy.release(); await pending; eq(busy.posts.length, 1, 'one completed request');
}
console.log(`site_r3_form_runtime_cases=${cases} assertions=${checks} real_network_calls=0`);
console.log('SITE_R3_FORM_RUNTIME_PASS');
