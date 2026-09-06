#!/usr/bin/env node
// Execute the shipped static calculator, not a second implementation in the test.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const source=read('components/BusinessValueCalculator.tsx');
const historical=read('scripts/check_r70_business_calculator.mjs');
const vectorText=historical.match(/const vectors = (\[[\s\S]*?\n\]);/);
assert.ok(vectorText,'Original vector set');
const vectors=vm.runInNewContext('('+vectorText[1]+')',{}, {timeout:1000});
assert.equal(vectors.length,20);
const arithmetic=['monthlyRoutine','recoverableHours','grossValue'].map(name=>{
 const match=source.match(new RegExp('const '+name+' = [^;]+;'));
 assert.ok(match,`Source arithmetic ${name}`); return match[0];
}).join('\n');
const sourceCalc=vm.runInNewContext('(function(team,weeklyHours,rate,recoverable){const WEEKS_PER_MONTH=52/12;'+arithmetic+'return {monthlyRoutine,recoverableHours,grossValue};})');
const attributes=tag=>Object.fromEntries([...tag.matchAll(/([\w-]+)="([^"]*)"/g)].map(m=>[m[1],m[2]]));
const ids=['bv-team','bv-hours','bv-rate','bv-recoverable'];
const limits=[[1,30,1],[1,40,1],[10,200,5],[10,80,5]];
let tested=0;
for(const locale of ['ru','en']) {
 const html=read(`deploy/live/${locale==='en'?'en/':''}business.html`);
 const block=html.match(/<script id="r98-business-calculator">([\s\S]*?)<\/script>/);
 assert.ok(block,`${locale}: shipped calculator script is missing`);
 assert.equal(html.split('data-business-value').length-1,2,`${locale}: exactly one mount and one runtime lookup`);
 for(const bad of ['fetch(','XMLHttpRequest','sendBeacon(','WebSocket(','localStorage','sessionStorage','document.cookie','https://t.me/']) assert.ok(!block[1].includes(bad),bad);
 const inputs=new Map(); const results=new Map(); const brief={textContent:''};
 for(const [index,id] of ids.entries()) {
  const tags=[...html.matchAll(/<input\b[^>]*>/g)].map(m=>m[0]).filter(x=>attributes(x).id===id);
  assert.equal(tags.length,1,`${locale}: input ${id}`);
  const a=attributes(tags[0]),[min,max,step]=limits[index];
  assert.equal(a.type,'range');assert.equal(Number(a.min),min);assert.equal(Number(a.max),max);assert.equal(Number(a.step||1),step);
  assert.ok(/\bdisabled(?:=|\s|\/?>)/.test(tags[0]),`${id}: safe no-JS initial state`);
  const label={textContent:''},events={};
  inputs.set(id,{value:a.value,disabled:true,events,addEventListener:(event,fn)=>{assert.equal(event,'input');assert.ok(!events[event]);events[event]=fn;},closest:tag=>{assert.equal(tag,'label');return {querySelector:s=>{assert.equal(s,'strong');return label;}};}});
 }
 for(const key of ['monthlyRoutine','recoverableHours','grossValue']) {
  assert.ok(html.includes(`data-bv-result="${key}"`),`${locale}: rendered ${key}`);
  results.set(key,{textContent:'',dataset:{}});
 }
 const widget={dataset:{locale},querySelector:selector=>{
  if(selector==='[data-bv-brief]')return brief;
  const m=selector.match(/^\[data-bv-result="([^"]+)"\]$/);assert.ok(m,selector);assert.ok(results.has(m[1]));return results.get(m[1]);
 }};
 const document={querySelector:s=>{assert.equal(s,'[data-business-value]');return widget;},getElementById:id=>inputs.get(id)};
 vm.runInNewContext(block[1],{document,Intl}, {timeout:1000});
 assert.ok([...inputs.values()].every(x=>!x.disabled&&typeof x.events.input==='function'));
 for(const v of vectors) {
  const values=[v.team,v.weeklyHours,v.rate,v.recoverable];
  values.forEach((value,index)=>{const input=inputs.get(ids[index]);input.value=String(value);input.events.input();});
  const expected=sourceCalc(...values);
  assert.ok(Math.abs(expected.grossValue-v.expectedGross)<1e-6,'Independent original vector');
  for(const key of results.keys()) {
   const actual=Number(results.get(key).dataset.value);
   assert.ok(Number.isFinite(actual)&&Math.abs(actual-expected[key])<1e-6,`${locale}: ${key}: ${actual} != ${expected[key]}`);
   assert.ok(results.get(key).textContent.startsWith('~'),`${locale}: visible result`);
  }
  const money=new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(expected.grossValue);
  assert.ok(results.get('grossValue').textContent.includes(money),'Visible gross value must update');
  assert.ok(brief.textContent.includes(money)&&brief.textContent.includes(v.recoverable+'%'),'Brief must track inputs');
  tested++;
 }
 const start=locale==='ru'?'/start#business-brief':'/en/start#business-brief';
 assert.ok(html.includes(`href="${start}"`),'Internal Start CTA');
 assert.ok(html.includes('<noscript>')&&html.includes('data-bv-brief'),'No-JS fallback and manual-copy brief');
 console.log(`calculator_runtime_${locale}=PASS vectors=${vectors.length} inputs=4 no_network=true`);
}
assert.equal(tested,40);
console.log('BUSINESS_CALCULATOR_SHIPPED_RUNTIME_PASS cases='+tested);
