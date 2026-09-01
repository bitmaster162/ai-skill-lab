#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LIVE = path.join(ROOT, 'deploy', 'live');
const LIVE_ROOT = path.resolve(LIVE);
const LIVE_PREFIX = LIVE_ROOT + path.sep;
const MAX_HTML_BR = 7 * 1024;
const MAX_CSS_BR = 8 * 1024;
const MAX_SHARED_JS_BR = 1 * 1024;
const MAX_FIRST_VIEW_BR = 16 * 1024;
const MAX_FIRST_VIEW_GZIP = 20 * 1024;
const IMPORT_RE = /@import\s+(?:url\()?[\"']?([^\"')\s;]+)/gi;
const LINK_RE = /<link\b[^>]*>/gi;
const SCRIPT_RE = /<script\b[^>]*>/gi;

const br = (buf) => zlib.brotliCompressSync(buf, { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 } }).length;
const gz = (buf) => zlib.gzipSync(buf, { level: 9 }).length;
const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
  const p = path.join(dir, e.name);
  return e.isDirectory() ? walk(p) : [p];
});
const sum = (items, fn) => items.reduce((n, item) => n + fn(item.buf), 0);

function attr(tag, name) {
  const quoted = tag.match(new RegExp(`\\b${name}\\s*=\\s*([\"'])(.*?)\\1`, 'i'));
  if (quoted) return quoted[2];
  const bare = tag.match(new RegExp(`\\b${name}\\s*=\\s*([^\\s>]+)`, 'i'));
  return bare ? bare[1] : null;
}

function localAsset(raw, fromFile, kind) {
  const clean = raw.split(/[?#]/, 1)[0];
  if (!clean) throw new Error(`${kind}: empty asset reference in ${path.relative(LIVE, fromFile)}`);
  if (/^[a-z][a-z0-9+.-]*:|^\/\//i.test(clean)) {
    throw new Error(`${kind}: external asset ${raw} in ${path.relative(LIVE, fromFile)}`);
  }
  const full = path.resolve(clean.startsWith('/') ? path.join(LIVE, clean.slice(1)) : path.resolve(path.dirname(fromFile), clean));
  if (full !== LIVE_ROOT && !full.startsWith(LIVE_PREFIX)) {
    throw new Error(`${kind}: asset escapes deploy/live ${raw} in ${path.relative(LIVE, fromFile)}`);
  }
  if (!fs.existsSync(full) || !fs.statSync(full).isFile()) {
    throw new Error(`${kind}: missing asset ${raw} in ${path.relative(LIVE, fromFile)}`);
  }
  return full;
}

function cssGraph(entry, seen = new Set()) {
  const full = path.resolve(entry);
  if (seen.has(full)) return [];
  if (full !== LIVE_ROOT && !full.startsWith(LIVE_PREFIX)) throw new Error(`invalid CSS import ${full}`);
  if (!fs.existsSync(full) || !fs.statSync(full).isFile()) throw new Error(`missing CSS import ${full}`);
  seen.add(full);
  const buf = fs.readFileSync(full);
  const text = buf.toString('utf8');
  const out = [{ path: full, buf }];
  IMPORT_RE.lastIndex = 0;
  for (let m; (m = IMPORT_RE.exec(text)); ) {
    const target = localAsset(m[1], full, 'css-import');
    out.push(...cssGraph(target, seen));
  }
  return out;
}

function pageAssets(page, html) {
  const cssEntries = [];
  LINK_RE.lastIndex = 0;
  for (let m; (m = LINK_RE.exec(html)); ) {
    const rel = (attr(m[0], 'rel') || '').toLowerCase().split(/\s+/).filter(Boolean);
    const href = attr(m[0], 'href');
    if (rel.includes('stylesheet') && href) cssEntries.push(localAsset(href, page, 'stylesheet'));
  }

  const cssSeen = new Set();
  const css = [];
  for (const entry of cssEntries) css.push(...cssGraph(entry, cssSeen));

  const jsSeen = new Set();
  const js = [];
  SCRIPT_RE.lastIndex = 0;
  for (let m; (m = SCRIPT_RE.exec(html)); ) {
    const src = attr(m[0], 'src');
    if (!src) continue;
    const full = localAsset(src, page, 'script');
    if (jsSeen.has(full)) continue;
    jsSeen.add(full);
    js.push({ path: full, buf: fs.readFileSync(full) });
  }
  return { css, js };
}

const errors = [];
let checks = 0;
const sharedLab = fs.readFileSync(path.join(LIVE, 'lab-command.js'));
const sharedLabBr = br(sharedLab);
checks++;
if (sharedLabBr > MAX_SHARED_JS_BR) errors.push(`lab-command.js brotli ${sharedLabBr} > ${MAX_SHARED_JS_BR}`);

let largestHtmlBr = { bytes: 0, route: '' };
let largestCssBr = { bytes: 0, route: '', files: 0 };
let largestJsBr = { bytes: 0, route: '', files: 0 };
let worstBr = { bytes: 0, route: '' };
let worstGz = { bytes: 0, route: '' };
const pages = walk(LIVE).filter((p) => p.endsWith('.html')).sort();

for (const page of pages) {
  const rel = path.relative(LIVE, page).replaceAll('\\', '/');
  const htmlBuf = fs.readFileSync(page);
  const html = htmlBuf.toString('utf8');
  const { css, js } = pageAssets(page, html);
  const htmlBr = br(htmlBuf);
  const htmlGz = gz(htmlBuf);
  const cssBr = sum(css, br);
  const cssGz = sum(css, gz);
  const jsBr = sum(js, br);
  const jsGz = sum(js, gz);
  const firstBr = htmlBr + cssBr + jsBr;
  const firstGz = htmlGz + cssGz + jsGz;

  checks++; if (htmlBr > MAX_HTML_BR) errors.push(`${rel}: HTML brotli ${htmlBr} > ${MAX_HTML_BR}`);
  checks++; if (cssBr > MAX_CSS_BR) errors.push(`${rel}: CSS brotli ${cssBr} > ${MAX_CSS_BR}`);
  checks++; if (firstBr > MAX_FIRST_VIEW_BR) errors.push(`${rel}: first-view brotli ${firstBr} > ${MAX_FIRST_VIEW_BR}`);
  checks++; if (firstGz > MAX_FIRST_VIEW_GZIP) errors.push(`${rel}: first-view gzip ${firstGz} > ${MAX_FIRST_VIEW_GZIP}`);

  if (htmlBr > largestHtmlBr.bytes) largestHtmlBr = { bytes: htmlBr, route: rel };
  if (cssBr > largestCssBr.bytes) largestCssBr = { bytes: cssBr, route: rel, files: css.length };
  if (jsBr > largestJsBr.bytes) largestJsBr = { bytes: jsBr, route: rel, files: js.length };
  if (firstBr > worstBr.bytes) worstBr = { bytes: firstBr, route: rel };
  if (firstGz > worstGz.bytes) worstGz = { bytes: firstGz, route: rel };
}

console.log(`transfer_performance_checks=${checks} pages=${pages.length} shared_lab_br=${sharedLabBr}`);
console.log(`largest_html_br=${largestHtmlBr.bytes} route=${largestHtmlBr.route} budget=${MAX_HTML_BR}`);
console.log(`largest_css_br=${largestCssBr.bytes} route=${largestCssBr.route} files=${largestCssBr.files} budget=${MAX_CSS_BR}`);
console.log(`largest_js_br=${largestJsBr.bytes} route=${largestJsBr.route} files=${largestJsBr.files}`);
console.log(`worst_first_view_br=${worstBr.bytes} route=${worstBr.route} budget=${MAX_FIRST_VIEW_BR}`);
console.log(`worst_first_view_gzip=${worstGz.bytes} route=${worstGz.route} budget=${MAX_FIRST_VIEW_GZIP}`);
if (errors.length) {
  console.log('TRANSFER_PERFORMANCE_FAIL');
  for (const error of errors) console.log('-', error);
  process.exit(1);
}
console.log('TRANSFER_PERFORMANCE_PASS');
