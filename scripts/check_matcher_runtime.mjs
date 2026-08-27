#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

class FakeElement {
  constructor({id='', classes=[], dataset={}, textContent='' } = {}) {
    this.id=id; this.classes=new Set(classes); this.dataset={...dataset}; this.textContent=textContent;
    this.attrs={}; this.listeners=new Map(); this.style={}; this.children=[]; this.value='';
  }
  addEventListener(type, fn) { this.listeners.set(type, fn); }
  setAttribute(k,v) { this.attrs[k]=String(v); }
  getAttribute(k) { return this.attrs[k] ?? null; }
  appendChild(el) { this.children.push(el); return el; }
  remove() {}
  select() {}
  closest() { return null; }
  async trigger(type='click') { const fn=this.listeners.get(type); if (!fn) throw new Error(`missing ${type} listener for ${this.id || JSON.stringify(this.dataset)}`); return await fn.call(this, {type,target:this}); }
}

function makeHarness(lang) {
  const options=[];
  const values={
    audience:['adult','kids','teens','business'],
    goal:['research','create','automate','team'],
    depth:['intro','core','deep'],
  };
  for (const [kind,vals] of Object.entries(values)) for (const value of vals) options.push(new FakeElement({classes:['mopt'],dataset:{kind,value},textContent:value}));

  const byId=new Map();
  const output=new FakeElement({id:'matcher-output'});
  let html='';
  Object.defineProperty(output,'innerHTML',{
    get(){ return html; },
    set(v){
      html=String(v);
      for (const id of ['mreset','mcopy']) {
        if (html.includes(`id="${id}"`)) byId.set(id,new FakeElement({id,textContent:id}));
        else byId.delete(id);
      }
      const tg=html.match(/<a class="btn light" id="mtelegram" href="([^"]+)" target="_blank" rel="noopener noreferrer">([^<]+)<\/a>/);
      if (tg) {
        const el=new FakeElement({id:'mtelegram',textContent:tg[2]});
        el.setAttribute('href',tg[1]); el.setAttribute('target','_blank'); el.setAttribute('rel','noopener noreferrer');
        byId.set('mtelegram',el);
      } else byId.delete('mtelegram');
    }
  });
  byId.set('matcher-output',output);
  let clipboard='';

  const document={
    documentElement:{lang},
    body:new FakeElement(),
    getElementById(id){ return byId.get(id) || null; },
    createElement(){ return new FakeElement(); },
    execCommand(){ return true; },
    querySelectorAll(selector){
      if (selector === '.mopt') return options;
      const m=selector.match(/^\.mopt\[data-kind="([^"]+)"\]$/);
      if (m) return options.filter(x=>x.dataset.kind===m[1]);
      return [];
    },
  };
  const context={
    document,
    navigator:{clipboard:{async writeText(text){ clipboard=String(text); }}},
    console,
    setTimeout(fn){ fn(); return 1; },
    clearTimeout(){},
  };
  context.window=context;
  return {context,options,output,getClipboard:()=>clipboard};
}

function extractInlineJs(file) {
  const html=fs.readFileSync(file,'utf8');
  const matches=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)];
  const js=matches.map(m=>m[1]).find(x=>x.includes('const S={audience:null'));
  if (!js) throw new Error(`matcher script not found in ${file}`);
  return js;
}

async function runCase(rel,lang) {
  const file=path.join(root,rel);
  const js=extractInlineJs(file);
  const h=makeHarness(lang);
  vm.runInNewContext(js,h.context,{filename:rel,timeout:1000});
  const pick=async (kind,value)=>{
    const el=h.options.find(x=>x.dataset.kind===kind && x.dataset.value===value);
    if (!el) throw new Error(`missing option ${kind}:${value}`);
    await el.trigger();
  };

  if (h.context.document.getElementById('mtelegram')) throw new Error(`${rel}: Telegram CTA must be absent before recommendation`);
  await pick('audience','adult');
  await pick('goal','research');
  await pick('depth','core');
  if (!h.output.innerHTML.includes('Personal') || !h.output.innerHTML.includes('$890')) throw new Error(`${rel}: adult/core recommendation mismatch`);
  const tg=h.context.document.getElementById('mtelegram');
  if (!tg) throw new Error(`${rel}: Telegram CTA not rendered`);
  const prefix='https://t.me/BiTFormer?text=';
  const href=tg.getAttribute('href') || '';
  if (!href.startsWith(prefix)) throw new Error(`${rel}: Telegram href prefix mismatch`);
  if (tg.getAttribute('target') !== '_blank') throw new Error(`${rel}: Telegram target mismatch`);
  const relTokens=new Set((tg.getAttribute('rel') || '').split(/\s+/));
  if (!relTokens.has('noopener') || !relTokens.has('noreferrer')) throw new Error(`${rel}: Telegram rel mismatch`);
  const copy=h.context.document.getElementById('mcopy');
  if (!copy) throw new Error(`${rel}: copy button not rendered`);
  await copy.trigger();
  const clip=h.getClipboard();
  if (!clip.includes('Personal') || !clip.includes('$890') || !clip.includes('\n')) throw new Error(`${rel}: copied brief incomplete`);
  if (lang==='ru' && !clip.includes('AI Skill Lab — запрос')) throw new Error(`${rel}: RU copied brief mismatch`);
  if (lang==='en' && !clip.includes('AI Skill Lab — request')) throw new Error(`${rel}: EN copied brief mismatch`);
  if (decodeURIComponent(href.slice(prefix.length)) !== clip) throw new Error(`${rel}: Telegram payload differs from copied brief`);

  const reset=h.context.document.getElementById('mreset');
  await reset.trigger();
  if (!h.output.innerHTML.includes(lang==='en' ? 'Choose one option' : 'Выберите по одному варианту')) throw new Error(`${rel}: reset did not restore empty state`);

  await pick('audience','business');
  await pick('goal','team');
  await pick('depth','deep');
  if (!h.output.innerHTML.includes('Business workflow pilot') || !h.output.innerHTML.includes('Custom scope')) throw new Error(`${rel}: business recommendation mismatch`);

  return {rel,checks:14,clipboardLines:clip.split('\n').length};
}

const results=[];
try {
  results.push(await runCase('deploy/live/matcher.html','ru'));
  results.push(await runCase('deploy/live/en/matcher.html','en'));
  const checks=results.reduce((n,x)=>n+x.checks,0);
  console.log(`matcher_runtime_checks=${checks} pages=${results.length}`);
  for (const r of results) console.log(`${r.rel}: PASS clipboard_lines=${r.clipboardLines}`);
  console.log('MATCHER_RUNTIME_SMOKE_PASS');
} catch (err) {
  console.error('FAIL:', err?.stack || err);
  process.exit(1);
}
