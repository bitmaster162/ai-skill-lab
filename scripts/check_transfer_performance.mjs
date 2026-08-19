#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const LIVE = path.join(ROOT, 'deploy', 'live');
const MAX_HTML_BR = 7 * 1024;
const MAX_CSS_BR = 8 * 1024;
const MAX_SHARED_JS_BR = 1 * 1024;
const MAX_FIRST_VIEW_BR = 16 * 1024;
const MAX_FIRST_VIEW_GZIP = 20 * 1024;
const IMPORT_RE = /@import\s+(?:url\()?["']?([^"')\s;]+)/gi;

const br = (buf) => zlib.brotliCompressSync(buf, { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 } }).length;
const gz = (buf) => zlib.gzipSync(buf, { level: 9 }).length;
const walk = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
  const p = path.join(dir, e.name);
  return e.isDirectory() ? walk(p) : [p];
});

function cssGraph(entry, seen = new Set()) {
  const full = path.resolve(entry);
  if (seen.has(full)) return [];
  const live = path.resolve(LIVE) + path.sep;
  if (!full.startsWith(live) || !fs.existsSync(full)) throw new Error(`invalid CSS import ${full}`);
  seen.add(full);
  const buf = fs.readFileSync(full);
  const text = buf.toString('utf8');
  const out = [{ path: full, buf }];
  IMPORT_RE.lastIndex = 0;
  for (let m; (m = IMPORT_RE.exec(text)); ) {
    const raw = m[1];
    if (/^[a-z][a-z0-9+.-]*:|^\/\//i.test(raw)) throw new Error(`external CSS import ${raw}`);
    const target = raw.startsWith('/') ? path.join(LIVE, raw.slice(1)) : path.resolve(path.dirname(full), raw);
    out.push(...cssGraph(target.split(/[?#]/, 1)[0], seen));
  }
  return out;
}

const cssFiles = cssGraph(path.join(LIVE, 'style.css'));
const lab = fs.readFileSync(path.join(LIVE, 'lab-command.js'));
const cssBr = cssFiles.reduce((n,x)=>n+br(x.buf),0);
const cssGz = cssFiles.reduce((n,x)=>n+gz(x.buf),0);
const cssRaw = cssFiles.reduce((n,x)=>n+x.buf.length,0);
const jsBr = br(lab), jsGz = gz(lab);
const errors = [];
let checks = 0;
checks++; if (cssBr > MAX_CSS_BR) errors.push(`stylesheet graph brotli ${cssBr} > ${MAX_CSS_BR}`);
checks++; if (jsBr > MAX_SHARED_JS_BR) errors.push(`lab-command.js brotli ${jsBr} > ${MAX_SHARED_JS_BR}`);

let worstBr = { bytes: 0, route: '' };
let worstGz = { bytes: 0, route: '' };
let largestHtmlBr = { bytes: 0, route: '' };
const pages = walk(LIVE).filter((p) => p.endsWith('.html')).sort();
for (const p of pages) {
  const rel = path.relative(LIVE, p).replaceAll('\\', '/');
  const html = fs.readFileSync(p);
  const htmlBr = br(html), htmlGz = gz(html);
  const firstBr = htmlBr + cssBr + jsBr;
  const firstGz = htmlGz + cssGz + jsGz;
  checks++; if (htmlBr > MAX_HTML_BR) errors.push(`${rel}: HTML brotli ${htmlBr} > ${MAX_HTML_BR}`);
  checks++; if (firstBr > MAX_FIRST_VIEW_BR) errors.push(`${rel}: first-view brotli ${firstBr} > ${MAX_FIRST_VIEW_BR}`);
  checks++; if (firstGz > MAX_FIRST_VIEW_GZIP) errors.push(`${rel}: first-view gzip ${firstGz} > ${MAX_FIRST_VIEW_GZIP}`);
  if (htmlBr > largestHtmlBr.bytes) largestHtmlBr = { bytes: htmlBr, route: rel };
  if (firstBr > worstBr.bytes) worstBr = { bytes: firstBr, route: rel };
  if (firstGz > worstGz.bytes) worstGz = { bytes: firstGz, route: rel };
}

console.log(`transfer_performance_checks=${checks} pages=${pages.length} css_files=${cssFiles.length} css_raw=${cssRaw} css_br=${cssBr} css_gz=${cssGz} shared_js_br=${jsBr} shared_js_gz=${jsGz}`);
console.log(`largest_html_br=${largestHtmlBr.bytes} route=${largestHtmlBr.route}`);
console.log(`worst_first_view_br=${worstBr.bytes} route=${worstBr.route} budget=${MAX_FIRST_VIEW_BR}`);
console.log(`worst_first_view_gzip=${worstGz.bytes} route=${worstGz.route} budget=${MAX_FIRST_VIEW_GZIP}`);
if (errors.length) {
  console.log('TRANSFER_PERFORMANCE_FAIL');
  for (const e of errors) console.log('-', e);
  process.exit(1);
}
console.log('TRANSFER_PERFORMANCE_PASS');
