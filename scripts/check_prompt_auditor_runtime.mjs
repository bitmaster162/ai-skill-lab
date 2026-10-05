#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const code=fs.readFileSync(path.join(ROOT,"deploy/live/prompt-auditor.js"),"utf8");
const failures=[]; let checks=0;
const req=(cond,msg)=>{checks++;if(!cond)failures.push(msg);};
class El {
  constructor(){this.value="";this.disabled=false;this.hidden=true;this.textContent="";this.listeners={};}
  addEventListener(type,fn){this.listeners[type]=fn;}
}
function makeRoot(locale){
  const el={input:new El(),run:new El(),message:new El(),result:new El(),score:new El(),explanation:new El(),improved:new El(),copy:new El()};
  const map={"[data-pa-input]":el.input,"[data-pa-run]":el.run,"[data-pa-message]":el.message,"[data-pa-result]":el.result,"[data-pa-score]":el.score,"[data-pa-explanation]":el.explanation,"[data-pa-improved]":el.improved,"[data-pa-copy]":el.copy};
  return {dataset:{locale},querySelector:(s)=>map[s]||null,el};
}
const ru=makeRoot("ru"), secret=makeRoot("en"), rate=makeRoot("en");
let calls=[]; let copied="";
const fetch=async(_url,opts)=>{
  const body=JSON.parse(opts.body); calls.push(body);
  if(body.prompt==="secret") return {ok:false,status:400,json:async()=>({status:"secret_detected"})};
  if(body.prompt==="rate") return {ok:false,status:429,json:async()=>({status:"rate_limited"})};
  return {ok:true,status:200,json:async()=>({status:"ok",score:8,improved:"Improved prompt",explanation:"Clearer scope"})};
};
vm.runInNewContext(code,{document:{querySelectorAll:()=>[ru,secret,rate]},fetch,navigator:{clipboard:{writeText:async(v)=>{copied=v;}}},console,Promise});
req(calls.length===0,"must not call API before user action");
ru.el.input.value="working prompt"; ru.el.input.listeners.input(); await ru.el.run.listeners.click();
req(calls.length===1&&calls[0].mode==="prompt_audit"&&calls[0].locale==="ru"&&calls[0].prompt==="working prompt","RU request contract");
req(ru.el.result.hidden===false&&ru.el.score.textContent==="8","RU score rendering");
req(ru.el.improved.textContent==="Improved prompt"&&ru.el.explanation.textContent==="Clearer scope","RU result rendering");
await ru.el.copy.listeners.click(); req(copied==="Improved prompt","copy improved prompt");
secret.el.input.value="secret"; secret.el.input.listeners.input(); await secret.el.run.listeners.click();
req(secret.el.result.hidden===true&&/secret|credential/i.test(secret.el.message.textContent),"secret fail-closed UI");
rate.el.input.value="rate"; rate.el.input.listeners.input(); await rate.el.run.listeners.click();
req(rate.el.result.hidden===true&&/limit/i.test(rate.el.message.textContent),"rate-limit UI");
console.log("a8_prompt_auditor_runtime_checks="+checks+" api_calls="+calls.length);
if(failures.length){console.log("A8_PROMPT_AUDITOR_RUNTIME_FAIL");for(const f of failures)console.log("FAIL:",f);process.exit(1);}
console.log("A8_PROMPT_AUDITOR_RUNTIME_PASS");
