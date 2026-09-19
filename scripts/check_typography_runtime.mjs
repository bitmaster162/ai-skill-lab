#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import crypto from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LIVE = path.join(ROOT, 'deploy', 'live');
const errors = [];
let checks = 0;
const req = (cond, msg) => { checks++; if (!cond) errors.push(msg); };

const expected = {
  'Onest-ru-en.woff2': { size: 30036, sha: '1527f4a5e3a2c65b9d789bf86a49cceefea2472bda0b1b3edc08b3adae4a9997' },
  'Unbounded-ru-en.woff2': { size: 52016, sha: '1600f2b8c27dc942601fdd2fc3f894f0375e371287d740289bf58945ab1991b1' },
};
for (const [name, meta] of Object.entries(expected)) {
  const deployed = path.join(LIVE, 'fonts', name);
  const source = path.join(ROOT, 'public', 'fonts', name);
  req(fs.existsSync(deployed), 'missing deploy/live/fonts/' + name);
  req(fs.existsSync(source), 'missing public/fonts/' + name);
  if (fs.existsSync(deployed)) {
    const buf = fs.readFileSync(deployed);
    req(buf.subarray(0, 4).toString('ascii') === 'wOF2', name + ': not WOFF2');
    req(buf.length === meta.size, name + ': bytes ' + buf.length + ' != ' + meta.size);
    req(crypto.createHash('sha256').update(buf).digest('hex') === meta.sha, name + ': SHA drift');
    if (fs.existsSync(source)) req(fs.readFileSync(source).equals(buf), name + ': public/static byte drift');
  }
}
for (const rel of ['licenses/Onest-OFL.txt', 'licenses/Unbounded-OFL.txt']) {
  const p = path.join(ROOT, rel);
  req(fs.existsSync(p), 'missing ' + rel);
  if (fs.existsSync(p)) req(fs.readFileSync(p, 'utf8').includes('SIL Open Font License, Version 1.1'), rel + ': OFL marker');
}

const css = fs.readFileSync(path.join(LIVE, 'workshop.css'), 'utf8');
const sourceCss = fs.readFileSync(path.join(ROOT, 'components', 'workshop', 'WorkshopShell.module.css'), 'utf8');
for (const marker of [
  '@font-face{font-family:"Onest"', 'font-weight:100 900', '@font-face{font-family:"Unbounded"',
  'font-weight:200 900', 'font-display:swap', 'font-family:"Onest"', 'font-family:"Unbounded"',
  'letter-spacing:-.01em', 'letter-spacing:-.005em', '.workshopUtility[data-lab-command-open]{column-gap:.25em}'
]) req(css.includes(marker), 'workshop.css missing ' + marker);
req(sourceCss.includes(':global(.labCommandTrigger){column-gap:.25em}'), 'source Lab Command gap missing');
for (const [text, label] of [[css, 'static CSS'], [sourceCss, 'source CSS']]) {
  const block = text.split('R115 Workshop v1 typography roles').slice(-1)[0];
  req(!block.includes('font-size:'), label + ': R115 overrides size scale');
  req(!text.includes('fonts.googleapis.com') && !text.includes('fonts.gstatic.com'), label + ': external font host');
}

const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
  const p = path.join(dir, e.name);
  return e.isDirectory() ? walk(p) : [p];
});
const htmls = walk(LIVE).filter((p) => p.endsWith('.html')).sort();
req(htmls.length === 47, 'html surfaces ' + htmls.length + ' != 47');
for (const hp of htmls) {
  const t = fs.readFileSync(hp, 'utf8');
  const rel = path.relative(LIVE, hp).replaceAll('\\', '/');
  req((t.match(/rel="preload" href="\/fonts\/Onest-ru-en\.woff2" as="font" type="font\/woff2" crossorigin/g) || []).length === 1, rel + ': Onest preload');
  req((t.match(/rel="preload" href="\/fonts\/Unbounded-ru-en\.woff2" as="font" type="font\/woff2" crossorigin/g) || []).length === 1, rel + ': Unbounded preload');
}

function mime(p) {
  if (p.endsWith('.css')) return 'text/css; charset=utf-8';
  if (p.endsWith('.woff2')) return 'font/woff2';
  if (p.endsWith('.js')) return 'text/javascript; charset=utf-8';
  return 'application/octet-stream';
}
const server = http.createServer((request, response) => {
  const u = new URL(request.url || '/', 'http://127.0.0.1');
  if (u.pathname === '/__typography_probe') {
    const lang = u.searchParams.get('lang') === 'en' ? 'en' : 'ru';
    const body = '<!doctype html><html lang="' + lang + '"><head><meta charset="utf-8"><link rel="stylesheet" href="/workshop.css"></head><body><div class="workshopPage"><main><section class="workshopHero"><h1 id="heading">Русский AI headline</h1><p id="copy">Body text</p><article class="priceCard"><strong id="price">$1,490</strong></article><button id="shortcut" class="workshopUtility" data-lab-command-open><span id="mod">Ctrl</span> K</button></section></main></div></body></html>';
    response.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Content-Length': Buffer.byteLength(body) });
    response.end(body);
    return;
  }
  const target = path.resolve(LIVE, '.' + decodeURIComponent(u.pathname));
  const livePrefix = LIVE + path.sep;
  if ((target !== LIVE && !target.startsWith(livePrefix)) || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
    response.writeHead(404); response.end('not found'); return;
  }
  const data = fs.readFileSync(target);
  response.writeHead(200, { 'Content-Type': mime(target), 'Content-Length': data.length });
  response.end(data);
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const serverPort = server.address().port;
const origin = 'http://127.0.0.1:' + serverPort;

function which(name) {
  const cmd = process.platform === 'win32' ? 'where' : 'which';
  const p = spawnSync(cmd, [name], { encoding: 'utf8' });
  if (p.status !== 0) return null;
  return (p.stdout || '').split(/\r?\n/).map((x) => x.trim()).find(Boolean) || null;
}
const candidates = [
  process.env.CHROME_BIN,
  which('google-chrome'),
  which('google-chrome-stable'),
  which('chromium'),
  which('chromium-browser'),
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
].filter(Boolean);
const chrome = candidates.find((p) => fs.existsSync(p));
req(Boolean(chrome), 'Chrome/Chromium not found');

let chromeProc = null;
let profile = null;
async function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
async function waitForFile(p, timeoutMs) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (fs.existsSync(p)) return;
    await sleep(50);
  }
  throw new Error('timeout waiting for ' + p);
}
async function openSocket(url) {
  const ws = new WebSocket(url);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = () => reject(new Error('WebSocket open failed'));
  });
  let seq = 0;
  const pending = new Map();
  const events = [];
  ws.onmessage = (event) => {
    const msg = JSON.parse(String(event.data));
    if (msg.id && pending.has(msg.id)) {
      const item = pending.get(msg.id); pending.delete(msg.id);
      if (msg.error) item.reject(new Error(JSON.stringify(msg.error))); else item.resolve(msg.result);
    } else if (msg.method) {
      events.push(msg);
    }
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++seq; pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
  return { ws, send, events };
}

if (chrome) {
  profile = fs.mkdtempSync(path.join(os.tmpdir(), 'asl-cdp-'));
  const args = [
    '--headless=new', '--disable-gpu', '--no-sandbox', '--remote-debugging-address=127.0.0.1',
    '--remote-debugging-port=0', '--user-data-dir=' + profile, 'about:blank'
  ];
  chromeProc = spawn(chrome, args, { stdio: 'ignore' });
  try {
    const active = path.join(profile, 'DevToolsActivePort');
    await waitForFile(active, 10000);
    const lines = fs.readFileSync(active, 'utf8').trim().split(/\r?\n/);
    const port = Number(lines[0]);
    const createUrl = 'http://127.0.0.1:' + port + '/json/new?about:blank';
    const created = await fetch(createUrl, { method: 'PUT' }).then((r) => r.json());
    const cdp = await openSocket(created.webSocketDebuggerUrl);
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Network.enable');

    for (const [lang, width, height] of [['ru', 1440, 900], ['ru', 390, 844], ['en', 1440, 900], ['en', 390, 844]]) {
      const beforeEvents = cdp.events.length;
      await cdp.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
      await cdp.send('Page.navigate', { url: origin + '/__typography_probe?lang=' + lang });
      const expression = '(async()=>{if(document.readyState==="loading")await new Promise(r=>document.addEventListener("DOMContentLoaded",r,{once:true}));await document.fonts.ready;const g=id=>getComputedStyle(document.getElementById(id));const sh=document.getElementById("shortcut"),mod=document.getElementById("mod"),tn=sh.childNodes[1],range=document.createRange();range.selectNodeContents(tn);return {fontCount:document.fonts.size,onest:document.fonts.check("400 16px Onest"),unbounded:document.fonts.check("600 32px Unbounded"),bodyFamily:getComputedStyle(document.body).fontFamily,hFamily:g("heading").fontFamily,pFamily:g("copy").fontFamily,priceFamily:g("price").fontFamily,hTrack:g("heading").letterSpacing,priceTrack:g("price").letterSpacing,shortcutGap:range.getBoundingClientRect().left-mod.getBoundingClientRect().right,columnGap:getComputedStyle(sh).columnGap};})()';
      const result = await cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
      const v = result.result && result.result.value ? result.result.value : {};
      req(Number(v.fontCount || 0) > 0, lang + '/' + width + ': document.fonts.size zero');
      req(v.onest === true, lang + '/' + width + ': Onest not loaded');
      req(v.unbounded === true, lang + '/' + width + ': Unbounded not loaded');
      req(String(v.bodyFamily || '').includes('Onest'), lang + '/' + width + ': body family ' + v.bodyFamily);
      req(String(v.hFamily || '').includes('Unbounded'), lang + '/' + width + ': h1 family ' + v.hFamily);
      req(String(v.pFamily || '').includes('Onest'), lang + '/' + width + ': p family ' + v.pFamily);
      req(String(v.priceFamily || '').includes('Unbounded'), lang + '/' + width + ': price family ' + v.priceFamily);
      req(String(v.hTrack || '') !== 'normal' && String(v.hTrack || '').startsWith('-'), lang + '/' + width + ': h1 tracking ' + v.hTrack);
      req(String(v.priceTrack || '') !== 'normal' && String(v.priceTrack || '').startsWith('-'), lang + '/' + width + ': price tracking ' + v.priceTrack);
      req(Number(v.shortcutGap || 0) > 1, lang + '/' + width + ': Ctrl/K gap ' + v.shortcutGap);
      req(v.columnGap !== 'normal' && v.columnGap !== '0px', lang + '/' + width + ': column gap ' + v.columnGap);

      const urls = cdp.events.slice(beforeEvents)
        .filter((e) => e.method === 'Network.requestWillBeSent')
        .map((e) => e.params && e.params.request ? e.params.request.url : '')
        .filter(Boolean);
      const external = urls.filter((u) => !u.startsWith(origin + '/') && !u.startsWith('data:'));
      req(external.length === 0, lang + '/' + width + ': external requests ' + JSON.stringify(external));
    }
    cdp.ws.close();
  } catch (e) {
    errors.push('CDP runtime: ' + (e && e.stack ? e.stack : String(e)));
  } finally {
    if (chromeProc && !chromeProc.killed) chromeProc.kill();
    await sleep(150);
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch {}
  }
}
await new Promise((resolve) => server.close(resolve));

console.log('typography_runtime_checks=' + checks + ' fonts=2 html=' + htmls.length + ' browser_cases=4');
if (errors.length) {
  console.log('WORKSHOP_TYPOGRAPHY_RUNTIME_FAIL');
  for (const e of errors) console.log('FAIL:', e);
  process.exit(1);
}
console.log('WORKSHOP_TYPOGRAPHY_RUNTIME_PASS');
