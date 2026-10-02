#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const js=fs.readFileSync(path.join(root,"deploy/live/matcher-v2.js"),"utf8");

class FakeElement{
  constructor({id="",classes=[],dataset={},textContent="",value="",checked=false}={}){
    this.id=id;this.classes=new Set(classes);this.dataset={...dataset};this.textContent=textContent;
    this.value=value;this.checked=checked;this.disabled=false;this.className="";this.attrs={};this.listeners=new Map();this.style={};this.children=[];
  }
  addEventListener(type,fn){this.listeners.set(type,fn)}
  setAttribute(k,v){this.attrs[k]=String(v)}
  getAttribute(k){return this.attrs[k]??null}
  appendChild(el){this.children.push(el);return el}
  remove(){}
  select(){}
  async trigger(type="click"){
    const fn=this.listeners.get(type);if(!fn)throw new Error(`missing ${type} listener for ${this.id||JSON.stringify(this.dataset)}`);
    return await fn.call(this,{type,target:this,preventDefault(){}});
  }
}

function makeHarness(lang,fetchImpl){
  const options=[];
  const values={audience:["adult","kids","teens","business"],goal:["research","create","automate","team"],depth:["intro","core","deep"]};
  for(const [kind,vals] of Object.entries(values))for(const value of vals)options.push(new FakeElement({classes:["mopt"],dataset:{kind,value},textContent:value}));
  const byId=new Map();
  const goal=new FakeElement({id:"matcher-goal"});
  const run=new FakeElement({id:"matcher-run",textContent:lang==="en"?"Find a route with AI":"Подобрать маршрут с AI"});
  const output=new FakeElement({id:"matcher-output"});
  let html="";
  Object.defineProperty(output,"innerHTML",{get(){return html},set(v){
    html=String(v);
    for(const id of ["mcopy","mreset","matcher-lead-form","matcher-lead-name","matcher-lead-contact","matcher-lead-consent","matcher-lead-adult","matcher-lead-submit","matcher-lead-message"])byId.delete(id);
    const ids=[...html.matchAll(/id="([^"]+)"/g)].map(x=>x[1]);
    for(const id of ids){
      if(byId.has(id))continue;
      const el=new FakeElement({id});
      if(id==="matcher-lead-submit")el.textContent=lang==="en"?"Send brief":"Отправить brief";
      byId.set(id,el);
    }
  }});
  byId.set("matcher-goal",goal);byId.set("matcher-run",run);byId.set("matcher-output",output);
  let clipboard="";
  const document={
    documentElement:{lang},body:new FakeElement(),
    getElementById(id){return byId.get(id)||null},
    createElement(){return new FakeElement()},
    execCommand(){return true},
    querySelectorAll(selector){
      if(selector===".mopt")return options;
      const m=selector.match(/^\.mopt\[data-kind="([^"]+)"\]$/);
      if(m)return options.filter(x=>x.dataset.kind===m[1]);
      return [];
    },
  };
  const calls=[];
  const context={
    document,
    navigator:{clipboard:{async writeText(text){clipboard=String(text)}}},
    console,
    fetch:async (url,opts)=>{calls.push({url,opts});return await fetchImpl(url,opts,calls)},
    setTimeout,clearTimeout,
  };
  context.window=context;
  vm.runInNewContext(js,context,{filename:"matcher-v2.js",timeout:1000});
  return {context,options,goal,run,output,byId,calls,getClipboard:()=>clipboard};
}

function apiResponse(body,status=200){return {ok:status>=200&&status<300,status,async json(){return body}}}
async function pick(h,kind,value){
  const el=h.options.find(x=>x.dataset.kind===kind&&x.dataset.value===value);
  if(!el)throw new Error(`missing option ${kind}:${value}`);
  await el.trigger();
}

let checks=0;
function req(cond,msg){checks+=1;if(!cond)throw new Error(msg)}

for(const rel of ["deploy/live/matcher.html","deploy/live/en/matcher.html"]){
  const html=fs.readFileSync(path.join(root,rel),"utf8");
  req(html.includes('id="matcher-goal"'),`${rel}: goal input missing`);
  req(html.includes('id="matcher-run"'),`${rel}: run button missing`);
  req(html.includes('src="/matcher-v2.js"'),`${rel}: external v2 runtime missing`);
  req(!html.includes("const S={audience:null"),`${rel}: legacy inline matcher returned`);
  req(html.includes("Бесплатный звонок-знакомство · 15 минут")||html.includes("Free 15-minute intro call"),`${rel}: intro-first surface missing`);
}

const adultResult={
  status:"ok",package:{id:"adult:personal",name:"Personal",price:"$890",sessions:"10 sessions"},
  steps:["Free 15-minute intro call","Diagnostic session $120 · 60 minutes · Credited toward a package purchased within 14 days.","Build one bounded research project."],
  brief:"Personal route brief."
};
const adult=makeHarness("en",async (url)=>{
  if(url==="/api/route")return apiResponse(adultResult);
  if(url==="/api/lead")return apiResponse({ok:true,requestId:"test"});
  throw new Error("unexpected URL "+url);
});
req(adult.calls.length===0,"network call before user action");
await pick(adult,"audience","adult");await pick(adult,"goal","research");await pick(adult,"depth","core");
adult.goal.value="Build a research workflow";await adult.goal.trigger("input");
req(adult.run.disabled===false,"run button stayed disabled");
await adult.run.trigger();
req(adult.calls.length===1&&adult.calls[0].url==="/api/route","route call mismatch");
const routePayload=JSON.parse(adult.calls[0].opts.body);
req(routePayload.audience==="adult","adult audience payload mismatch");
req(JSON.stringify(routePayload.answers)===JSON.stringify(["adult","research","core"]),"answers[3] payload mismatch");
req(routePayload.goal==="Build a research workflow","goal payload mismatch");
req(adult.output.innerHTML.includes("Personal")&&adult.output.innerHTML.includes("$890"),"AI package render mismatch");
req(adult.output.innerHTML.includes("Free 15-minute intro call"),"intro-first result missing");
req(adult.output.innerHTML.includes("Diagnostic session $120"),"diagnostic-second result missing");
await adult.byId.get("mcopy").trigger();
req(adult.getClipboard()==="Personal route brief.","brief copy mismatch");
adult.byId.get("matcher-lead-name").value="Synthetic Adult";
adult.byId.get("matcher-lead-contact").value="@synthetic";
adult.byId.get("matcher-lead-consent").checked=true;
await adult.byId.get("matcher-lead-form").trigger("submit");
req(adult.calls.length===2&&adult.calls[1].url==="/api/lead","lead call missing after consent");
const leadPayload=JSON.parse(adult.calls[1].opts.body);
req(leadPayload.goal==="Personal route brief.","lead goal must equal AI brief");
req(leadPayload.privacyConsent==="yes","privacy consent payload missing");

const kid=makeHarness("en",async (url)=>{
  if(url==="/api/route")return apiResponse({status:"error"},503);
  if(url==="/api/lead")return apiResponse({ok:true});
  throw new Error("unexpected URL "+url);
});
await pick(kid,"audience","kids");await pick(kid,"goal","create");await pick(kid,"depth","intro");
kid.goal.value="Creative project for a 10-year-old";await kid.goal.trigger("input");await kid.run.trigger();
req(kid.calls.length===1,"kids route should make one route call");
req(kid.output.innerHTML.includes("Mini")&&kid.output.innerHTML.includes("$290"),"kids fallback package mismatch");
req(kid.output.innerHTML.includes("AI routing is unavailable"),"fallback disclosure missing");
req(Boolean(kid.byId.get("matcher-lead-adult")),"youth adult confirmation missing");
kid.byId.get("matcher-lead-name").value="Synthetic Parent";kid.byId.get("matcher-lead-contact").value="@parent";kid.byId.get("matcher-lead-consent").checked=true;
await kid.byId.get("matcher-lead-form").trigger("submit");
req(kid.calls.length===1,"youth brief sent without adult confirmation");
kid.byId.get("matcher-lead-adult").checked=true;await kid.byId.get("matcher-lead-form").trigger("submit");
req(kid.calls.length===2&&kid.calls[1].url==="/api/lead","youth brief not sent after adult confirmation");
const kidLead=JSON.parse(kid.calls[1].opts.body);
req(kidLead.audience==="parent"&&kidLead.adultConfirmation==="yes","youth lead contract mismatch");

const secret=makeHarness("ru",async()=>{throw new Error("secret must not hit fetch")});
await pick(secret,"audience","adult");await pick(secret,"goal","research");await pick(secret,"depth","core");
secret.goal.value="Используй sk-proj-TEST123456789";await secret.goal.trigger("input");await secret.run.trigger();
req(secret.calls.length===0,"secret reached network");
req(secret.output.innerHTML.includes("секрет"),"secret warning not rendered");

console.log(`matcher_runtime_checks=${checks} pages=2 ai_success=1 fallback=1 secret_preflight=1 lead_consent=2`);
console.log("MATCHER_RUNTIME_SMOKE_PASS");
