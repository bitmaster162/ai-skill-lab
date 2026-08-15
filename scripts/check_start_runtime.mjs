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

function extract(file){const html=fs.readFileSync(file,'utf8');const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m=>m[1]);const js=scripts.find(x=>x.includes('document.querySelectorAll(".briefCopy")'));if(!js)throw new Error(`brief copy script not found: ${file}`);return js;}

async function run(rel,lang){
  const isEn=lang==='en';
  const specs=isEn?[
    ['Personal program',['Goal for the next 1–3 months','Which tasks repeat today','Which AI tools you already use','Online / Phuket · RU / EN']],
    ['For a child',['Age','What the child is interested in','Any AI experience','What project could engage them']],
    ['For a teen',['Age and current level','Interests: code / design / science / content / business','What they already tried with AI','What portfolio outcome would be useful']],
    ['Workflow pilot',['Which process you want to improve','Who performs and owns it','How often it repeats','What good output means / what happens on failure']],
  ]:[
    ['Личная программа',['Цель на ближайшие 1–3 месяца','Какие задачи повторяются сейчас','Какие AI-инструменты уже используете','Online / Phuket · RU / EN']],
    ['Для ребёнка',['Возраст','Что ребёнку интересно','Есть ли опыт с AI','Какой проект мог бы увлечь']],
    ['Для подростка',['Возраст и текущий уровень','Интересы: code / design / science / content / business','Что уже пробовал с AI','Какой portfolio outcome был бы полезен']],
    ['Workflow pilot',['Какой процесс хотите улучшить','Кто его выполняет и кто владелец','Как часто он повторяется','Что считается хорошим выходом / что будет при ошибке']],
  ];
  const initial=isEn?'Copy brief':'Скопировать brief';
  const buttons=[];
  for(const [title,lines] of specs){const card=new Card(title,lines);buttons.push(new E({textContent:initial,card}));}
  let clipboard=''; const timers=[];
  const document={documentElement:{lang},body:{appendChild(){}},querySelectorAll(sel){return sel==='.briefCopy'?buttons:[]},createElement(){return new E()},execCommand(){return true}};
  const navigator={clipboard:{async writeText(t){clipboard=String(t)}}};
  const context={document,navigator,setTimeout(fn){timers.push(fn);return timers.length},clearTimeout(){},console};context.window=context;
  vm.runInNewContext(extract(path.join(root,rel)),context,{filename:rel,timeout:1000});
  let checks=0;
  for(let i=0;i<buttons.length;i++){
    clipboard=''; await buttons[i].trigger();
    const [title,lines]=specs[i];
    if(!clipboard.includes(isEn?'AI Skill Lab — brief':'AI Skill Lab — запрос'))throw new Error(`${rel} card${i+1}: missing heading`); checks++;
    if(!clipboard.includes(title))throw new Error(`${rel} card${i+1}: missing route title`); checks++;
    for(const line of lines) if(!clipboard.includes(line))throw new Error(`${rel} card${i+1}: missing field ${line}`);
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
  console.log('START_RUNTIME_SMOKE_PASS');
}catch(err){console.error('FAIL:',err?.stack||err);process.exit(1)}
