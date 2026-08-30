#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import process from 'node:process';

const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');

class E {
  constructor({textContent='',card=null}={}){this.textContent=textContent;this.card=card;this.listeners=new Map();this.style={};this.value='';}
  addEventListener(t,fn,options=false){const list=this.listeners.get(t)||[];list.push({fn,capture:options===true||Boolean(options?.capture)});this.listeners.set(t,list)}
  closest(sel){return sel==='.card'?this.card:null}
  setAttribute(){}
  select(){}
  remove(){}
  async trigger(){
    const list=[...(this.listeners.get('click')||[])];
    const ordered=[...list.filter(x=>x.capture),...list.filter(x=>!x.capture)];
    const event={target:this,stopped:false,stopImmediatePropagation(){this.stopped=true}};
    for(const {fn} of ordered){await fn.call(this,event);if(event.stopped)break}
  }
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
  const inline=scripts.find(x=>x.includes('document.querySelectorAll(".briefCopy")'));
  if(inline)throw new Error(`brief copy runtime must be externalized: ${file}`);
  if(!html.includes('<script src="/start-brief.js"></script>'))throw new Error(`brief copy external script missing: ${file}`);
  const js=fs.readFileSync(path.join(root,'deploy/live/start-brief.js'),'utf8');
  if(!js.includes('document.querySelectorAll(".briefCopy")'))throw new Error('start-brief.js runtime missing');
  const blocks=[...html.matchAll(/<article class="card"(?: id="(?:studio|business)-brief")?>([\s\S]*?)<\/article>/gi)].map(m=>m[1]);
  if(blocks.length!==5)throw new Error(`${file}: expected 5 brief cards, got ${blocks.length}`);
  const cards=blocks.map((block,i)=>{
    const h=block.match(/<h3>([\s\S]*?)<\/h3>/i);
    const list=block.match(/<div class="checklist">([\s\S]*?)<\/div><div class="briefCardActions">/i);
    if(!h||!list)throw new Error(`${file}: card${i+1} structure drift`);
    const title=cleanText(h[1]);
    const lines=[...list[1].matchAll(/<div>\s*\d+\.\s*([\s\S]*?)<\/div>/gi)].map(x=>cleanText(x[1]));
    const expectedFields=i===4?6:4;
    if(lines.length!==expectedFields)throw new Error(`${file}: card${i+1} expected ${expectedFields} fields, got ${lines.length}`);
    const link=block.match(/<a class="btn briefTelegramLink" href="([^"]+)" target="_blank" rel="noopener noreferrer">([^<]+)<\/a>/i);
    if(!link)throw new Error(`${file}: card${i+1} missing exact Telegram brief link`);
    return {title,lines,href:link[1],label:cleanText(link[2])};
  });
  return {html,js,cards};
}

function attributionScript(){
  const full=fs.readFileSync(path.join(root,'deploy/live/lab-command.js'),'utf8');
  const marker='(()=>{"use strict";const START_PATHS=';
  const at=full.indexOf(marker);
  if(at<0)throw new Error('start source attribution runtime missing from lab-command.js');
  const js=full.slice(at);
  for(const forbidden of ['localStorage','sessionStorage','document.cookie','fetch(','XMLHttpRequest','sendBeacon']){
    if(js.includes(forbidden))throw new Error(`start attribution must stay storage/network free: ${forbidden}`);
  }
  return js;
}

function assertSourceParity(){
  const src=fs.readFileSync(path.join(root,'components/CopyBriefButton.tsx'),'utf8');
  const required=[
    'getSameOriginSource()',
    'referrer.origin !== window.location.origin',
    'path === "/start" || path === "/en/start"',
    'setSource(getSameOriginSource())',
    '`${isEn ? "Source" : "Источник"}: ${source}`',
  ];
  for(const token of required)if(!src.includes(token))throw new Error(`CopyBriefButton source-attribution parity missing: ${token}`);
  for(const forbidden of ['localStorage','sessionStorage','document.cookie','fetch(','XMLHttpRequest','sendBeacon']){
    if(src.includes(forbidden))throw new Error(`CopyBriefButton attribution must stay storage/network free: ${forbidden}`);
  }
  return required.length+6;
}

function buildBrief(title,lines,isEn,source=''){
  return [
    isEn?'AI Skill Lab — brief':'AI Skill Lab — запрос',
    `${isEn?'Route':'Маршрут'}: ${title}`,
    ...(source?[`${isEn?'Source':'Источник'}: ${source}`]:[]),
    ...lines.map((line,index)=>`${index+1}. ${line}: `),
  ].join('\n');
}

async function run(rel,lang,{referrer='',source=''}={}){
  const file=path.join(root,rel);
  const {js,cards}=extract(file);
  const sourceJs=attributionScript();
  const isEn=lang==='en';
  const initial=isEn?'Copy brief':'Скопировать brief';
  const expectedLabel=isEn?'Open Telegram with this brief →':'Написать в Telegram с brief →';
  const expectedStudioLines=isEn?[
    'What you want to build or change',
    'What happens today / what already exists',
    'Who will use it and who owns the outcome',
    'What counts as done / where failure would be costly',
  ]:[
    'Что хотите собрать или изменить',
    'Что происходит сейчас / что уже есть',
    'Кто будет пользоваться и кто владелец результата',
    'Что считается готовым / где ошибка будет критична',
  ];
  const expectedBusinessLines=isEn?[
    'Which process you want to improve',
    'Who performs and owns it',
    'How often it repeats',
    'Which inputs it uses',
    'What a good output looks like',
    'What happens if AI is wrong',
  ]:[
    'Какой процесс хотите улучшить',
    'Кто его выполняет и кто владелец',
    'Как часто он повторяется',
    'Какие входные данные используются',
    'Что считается хорошим выходом',
    'Что произойдёт, если AI ошибётся',
  ];
  let checks=0;
  const studio=cards[3];
  if(studio.title!=='AI Studio / build')throw new Error(`${rel}: card4 must be AI Studio / build`); checks++;
  if(JSON.stringify(studio.lines)!==JSON.stringify(expectedStudioLines))throw new Error(`${rel}: AI Studio brief fields drift`); checks++;
  const business=cards[4];
  if(business.title!=='Workflow pilot')throw new Error(`${rel}: AI Studio must remain immediately before BUSINESS`); checks++;
  if(JSON.stringify(business.lines)!==JSON.stringify(expectedBusinessLines))throw new Error(`${rel}: BUSINESS brief fields drift`); checks++;

  const buttons=cards.map(({title,lines})=>new E({textContent:initial,card:new Card(title,lines)}));
  const anchors=cards.map(({href})=>({href}));
  let clipboard=''; const timers=[];
  const pagePath=isEn?'/en/start':'/start';
  const pageUrl=new URL(`https://ai-skill-lab.vercel.app${pagePath}`);
  const document={
    documentElement:{lang},referrer,
    body:{appendChild(){}},
    querySelectorAll(sel){if(sel==='.briefCopy')return buttons;if(sel==='.briefTelegramLink')return anchors;return[]},
    createElement(){return new E()},execCommand(){return true},
  };
  const navigator={clipboard:{async writeText(t){clipboard=String(t)}}};
  const location={origin:pageUrl.origin,pathname:pageUrl.pathname};
  const context={document,navigator,location,URL,setTimeout(fn){timers.push(fn);return timers.length},clearTimeout(){},console};context.window=context;
  vm.runInNewContext(js,context,{filename:rel,timeout:1000});
  vm.runInNewContext(sourceJs,context,{filename:'deploy/live/lab-command.js#start-source-attribution',timeout:1000});

  for(let i=0;i<cards.length;i++){
    const {title,lines,label}=cards[i];
    const expected=buildBrief(title,lines,isEn,source);
    const href=anchors[i].href;
    const u=new URL(href);
    if(u.protocol!=='https:'||u.hostname!=='t.me'||u.pathname!=='/BiTFormer')throw new Error(`${rel} card${i+1}: Telegram route drift`); checks++;
    if(u.searchParams.get('text')!==expected)throw new Error(`${rel} card${i+1}: decoded Telegram brief/source differs from expected bytes`); checks++;
    if(label!==expectedLabel)throw new Error(`${rel} card${i+1}: Telegram CTA label drift`); checks++;

    clipboard=''; await buttons[i].trigger();
    if(clipboard!==expected)throw new Error(`${rel} card${i+1}: copied brief/source differs from expected bytes`); checks++;
    if(clipboard.split('\n').length!==lines.length+(source?3:2))throw new Error(`${rel} card${i+1}: unexpected brief line count`); checks++;
    if(source && clipboard.split('\n')[2]!==`${isEn?'Source':'Источник'}: ${source}`)throw new Error(`${rel} card${i+1}: source line position drift`); checks++;
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

  return {rel,checks,source:source||'NONE'};
}

try{
  let checks=assertSourceParity();
  const cases=[];
  for(const [rel,lang] of [['deploy/live/start.html','ru'],['deploy/live/en/start.html','en']]){
    cases.push(await run(rel,lang));
    cases.push(await run(rel,lang,{referrer:'https://example.com/pricing'}));
    cases.push(await run(rel,lang,{referrer:'https://ai-skill-lab.vercel.app/start'}));
    cases.push(await run(rel,lang,{referrer:'https://ai-skill-lab.vercel.app/pricing?from=cta#plans',source:'/pricing'}));
    cases.push(await run(rel,lang,{referrer:'https://ai-skill-lab.vercel.app/',source:'/'}));
  }
  checks+=cases.reduce((n,x)=>n+x.checks,0);
  console.log(`start_runtime_checks=${checks} cases=${cases.length}`);
  cases.forEach(x=>console.log(`${x.rel}: PASS source=${x.source} checks=${x.checks}`));
  console.log('START_RUNTIME_TELEGRAM_PREFILL_SOURCE_ATTRIBUTION_PASS');
}catch(err){console.error('FAIL:',err?.stack||err);process.exit(1)}
