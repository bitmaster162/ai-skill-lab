#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const full=fs.readFileSync(path.join(root,"deploy/live/lab-command.js"),"utf8");
const marker='(()=>{let l=document.documentElement.lang,p=location.pathname,f=e=>fetch("/api/event"';
const at=full.indexOf(marker);
if(at<0) throw new Error("E3.8 runtime marker missing");
const js=full.slice(at);

const listeners=new Map(),calls=[];
const document={documentElement:{lang:"ru"}};
const location={pathname:"/pricing",origin:"https://aiskillab.work"};
const fetch=async(url,opts)=>{calls.push({url,opts});return{ok:true}};
const ctx={document,location,fetch,URL,console};
ctx.window=ctx;
ctx.addEventListener=(type,fn)=>listeners.set(type,fn);
vm.runInNewContext(js,ctx,{timeout:1000});

const anchors=[
 [{protocol:"https:",hostname:"cal.com"},"cal_click"],
 [{protocol:"https:",hostname:"t.me"},"telegram_click"],
 [{protocol:"https:",hostname:"wa.me"},"whatsapp_click"],
 [{protocol:"https:",hostname:"line.me"},"line_click"],
 [{protocol:"mailto:",hostname:""},"email_click"],
];
for(const [anchor] of anchors){
  listeners.get("click")({target:{closest(){return anchor}}});
}
for(const event of ["lead_submit_ok","lead_submit_error"]){
  listeners.get("asl:lead-event")({detail:{event}});
}
if(calls.length!==7) throw new Error(`event calls ${calls.length} != 7`);
const expected=[...anchors.map(x=>x[1]),"lead_submit_ok","lead_submit_error"];
calls.forEach((call,i)=>{
  if(call.url!=="/api/event") throw new Error("event endpoint");
  if(call.opts.method!=="POST"||call.opts.credentials!=="omit"||!call.opts.keepalive) throw new Error("request policy");
  const body=JSON.parse(call.opts.body);
  if(JSON.stringify(Object.keys(body).sort())!==JSON.stringify(["event","locale","page"])) throw new Error("payload keys");
  if(body.event!==expected[i]||body.page!=="/pricing"||body.locale!=="ru") throw new Error("payload values");
  for(const forbidden of ["name","contact","goal","text","cookie"]) if(forbidden in body) throw new Error("forbidden payload "+forbidden);
});
console.log("E3_8_EVENT_RUNTIME_PASS calls=7 payload_keys=event,locale,page credentials=omit");
