#!/usr/bin/env node
/* Offline mock of the dormant Universe tracker. Never sends real network. */
import fs from "node:fs";
import vm from "node:vm";
import assert from "node:assert/strict";
const path=new URL("../../public/phuket-universe-events.js",import.meta.url);
const source=fs.readFileSync(path,"utf8");
assert.equal(source.includes("const ENABLED = false;"),true);
assert.equal(source.includes("localStorage"),false);
assert.equal(source.includes("sessionStorage"),false);
assert.equal(source.includes("document.cookie"),false);
function harness(active,locale="ru",page="/phuket") {
  const listeners=[],requests=[];
  const document={
    documentElement:{lang:locale},
    addEventListener(name,fn){listeners.push({name,fn});},
  };
  const context={document,URL,location:{origin:"https://aiskillab.work",pathname:page},
    fetch(url,options){requests.push({url,options});return Promise.resolve({ok:true});},
    console};
  context.globalThis=context;
  const code=active?source.replace("const ENABLED = false;","const ENABLED = true;"):source;
  vm.runInNewContext(code,context,{timeout:2000});
  return {
    listeners,requests,context,
    click(kind,href,{inOrbit=false,inListing=false}={}) {
      const anchor={
        getAttribute(key){return key==="data-universe-event"?kind:key==="href"?href:null;},
        closest(key){return (key==="#orbit"&&inOrbit)||(key==="#homes [data-u2-card]"&&inListing)?{}:null;}
      };
      for(const l of listeners.filter(l=>l.name==="click")){
        l.fn({target:{closest(key){return key==="a[data-universe-event]"?anchor:null;}}});
      }
    }
  };
}
const disabled=harness(false);
disabled.click("universe_click","/phuket-universe");
assert.equal(disabled.listeners.length,0);
assert.equal(disabled.requests.length,0);
let count=0;
for(const locale of ["ru","en"]){
  const h=harness(true,locale,locale==="ru"?"/phuket":"/en/phuket");
  const local=locale==="ru"?"/phuket-universe":"/en/phuket-universe";
  h.click("universe_click",local);
  h.click("project_click","https://phuketravel.vercel.app",{inOrbit:true});
  h.click("listing_click","https://agency.example.test/listing/id/1",{inListing:true});
  const before=h.requests.length;
  for(const bad of [
    ["universe_click","https://evil.example/phuket-universe",{}],
    ["project_click","https://evil.example", {inOrbit:true}],
    ["project_click","https://phuketravel.vercel.app",{}],
    ["listing_click","http://agency.example.test/listing",{inListing:true}],
    ["listing_click","https://agency.example.test/listing",{}],
    ["something_else",local,{}],
  ])h.click(bad[0],bad[1],bad[2]);
  assert.equal(h.requests.length,before);
  assert.equal(h.requests.length,3);
  assert.deepEqual(h.requests.map(x=>JSON.parse(x.options.body).event),
    ["universe_click","project_click","listing_click"]);
  for(const call of h.requests){
    assert.equal(call.url,"/api/event");
    assert.equal(call.options.method,"POST");
    assert.equal(call.options.credentials,"omit");
    assert.equal(call.options.keepalive,true);
    const payload=JSON.parse(call.options.body);
    assert.deepEqual(Object.keys(payload).sort(),["event","locale","page"]);
    assert.equal(payload.locale,locale);
    assert.equal(payload.page,locale==="ru"?"/phuket":"/en/phuket");
    for(const key of ["id","href","source_name","contact","cookie","listing_id","price","url"]){
      assert.equal(Object.hasOwn(payload,key),false);
    }
  }
  vm.runInNewContext(source.replace("const ENABLED = false;","const ENABLED = true;"),
    h.context,{timeout:2000});
  assert.equal(h.listeners.length,1,"no duplicate listeners on Next navigation");
  count+=h.requests.length;
}
console.log("UNIVERSE_EVENT_OFFLINE_PASS disabled_posts=0 enabled_mock_only="+count+
  " payload=event,page,locale malformed_rejected=12");
