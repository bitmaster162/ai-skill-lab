#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import process from 'node:process';

const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');

class E {
  constructor({textContent='',card=null}={}){this.textContent=textContent;this.card=card;this.listeners=new Map();this.style={};this.value='';}
  addEventListener(t,fn){this.listeners.set(t,fn)}
  closest(sel){return sel==='.card'?this.card:null}
  setAttribute(){}
  select(){}
  remove(){}
  async trigger(){const fn=this.listeners.get('click');if(!fn)throw new Error('missing click listener');return await fn.call(this,{target:this})}
}
class Card {
  constructor(title,lines){this.title=new E({textContent:title});this.lines=lines.map(x=>new E({textContent:x}));}
  querySelector(sel){return sel==='h3'?this.title:null}
  querySelectorAll(sel){return sel==='.checklist div'?this.lines:[]}
}

function cleanText(s){
  return s.replace(/<[^>]*>/g,'').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').trim();
}

function extract(file){
  const html=fs.readFileSync(file,'utf8');
  const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m=>m[1]);
  const js=scripts.find(x=>x.includes('document.querySelectorAll(".briefCopy")'));
  if(!js)throw new Error(`brief copy script not found: ${file}`);
  const blocks=[...html.matchAll(/<article class="card">([\s\S]*?)<\/article>/gi)].map(m=>m[1]);
  if(blocks.length!==4)throw new Error(`${file}: expected 4 brief cards, got ${blocks.length}`);
  const cards=blocks.map((block,i)=>{
    const h=block.match(/<h3>([\s\S]*?)<\/h3>/i);
    const list=block.match(/<div class="checklist">([\s\S]*?)<\/div><div class="briefCardActions">/i);
    if(!h||!list)throw new Error(`${file}: card${i+1} structure drift`);
    const title=cleanText(h[1]);
    const lines=[...list[1].matchAll(/<div>\s*\d+\.\s*([\s\S]*?)<\/div>/gi)].map(x=>cleanText(x[1]));
    if(lines.length!==4)throw new Error(`${file}: card${i+1} expected 4 fields, got ${lines.length}`);
    const link=block.match(/<a class="btn briefTelegramLink" href="([^"]+)" target="_blank" rel="noopener noreferrer">([^<]+)<\/a>/i);
    if(!link)throw new Error(`${file}: card${i+1} missing exact Telegram brief link`);
    return {title,lines,href:link[1],label:cleanText(link[2])};
  });
  return {html,js,cards};
}

function buildBrief(title,lines,isEn){
  return [
    isEn?'AI Skill Lab — brief':'AI Skill Lab — запрос',
    `${isEn?'Route':'Маршрут'}: ${title}`,
    ...lines.map((line,index)=>`${index+1}. ${line}: `),
  ].join('\n');
}

async function run(rel,lang){
  const file=path.join(root,rel);
  const {js,cards}=extract(file);
  const isEn=lang==='en';
  const initial=isEn?'Copy brief':'Скопировать brief';
  const expectedLabel=isEn?'Open Telegram with this brief →':'Написать в Telegram с brief →';
  let checks=0;

  const buttons=cards.map(({title,lines})=>new E({textContent:initial,card:new Card(title,lines)}));
  let clipboard=''; const timers=[];
  const document={documentElement:{lang},body:{appendChild(){}},querySelectorAll(sel){return sel==='.briefCopy'?buttons:[]},createElement(){return new E()},execCommand(){return true}};
  const navigator={clipboard:{async writeText(t){clipboard=String(t)}}};
  const context={document,navigator,setTimeout(fn){timers.push(fn);return timers.length},clearTimeout(){},console};context.window=context;
  vm.runInNewContext(js,context,{filename:rel,timeout:1000});

  for(let i=0;i<cards.length;i++){
    const {title,lines,href,label}=cards[i];
    const expected=buildBrief(title,lines,isEn);

    const u=new URL(href);
    if(u.protocol!=='https:'||u.hostname!=='t.me'||u.pathname!=='/BiTFormer')throw new Error(`${rel} card${i+1}: Telegram route drift`); checks++;
    if(!href.startsWith('https://t.me/BiTFormer?text='))throw new Error(`${rel} card${i+1}: Telegram prefix drift`); checks++;
    if(u.searchParams.get('text')!==expected)throw new Error(`${rel} card${i+1}: decoded Telegram brief differs from card bytes`); checks++;
    if(label!==expectedLabel)throw new Error(`${rel} card${i+1}: Telegram CTA label drift`); checks++;

    clipboard=''; await buttons[i].trigger();
    if(clipboard!==expected)throw new Error(`${rel} card${i+1}: copied brief differs from card bytes`); checks++;
    if(clipboard.split('\n').length!==6)throw new Error(`${rel} card${i+1}: expected 6 brief lines`); checks++;
    if(buttons[i].textContent !== (isEn?'Copied ✓':'Скопировано ✓'))throw new Error(`${rel} card${i+1}: missing success feedback`); checks++;
    while(timers.length) timers.shift()();
    if(buttons[i].textContent!==initial)throw new Error(`${rel} card${i+1}: success label did not reset`); checks++;
  }

  navigator.clipboard.writeText=async()=>{throw new Error('clipboard denied')};
  document.execCommand=()=>false;
  await buttons[0].trigger();
  if(buttons[0].textContent !== (isEn?'Copy failed':'Не удалось скопировать'))throw new Error(`${rel}: missing failure feedback`); checks++;
  while(timers.length) timers.shift()();
  if(buttons[0].textContent!==initial)throw new Error(`${rel}: failure label did not reset`); checks++;

  return {rel,checks};
}

try{
  const results=[await run('deploy/live/start.html','ru'),await run('deploy/live/en/start.html','en')];
  console.log(`start_runtime_checks=${results.reduce((n,x)=>n+x.checks,0)} pages=${results.length}`);
  results.forEach(x=>console.log(`${x.rel}: PASS checks=${x.checks}`));
  console.log('START_RUNTIME_TELEGRAM_PREFILL_PASS');
}catch(err){console.error('FAIL:',err?.stack||err);process.exit(1)}
