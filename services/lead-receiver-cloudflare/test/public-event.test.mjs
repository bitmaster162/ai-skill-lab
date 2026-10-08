import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { test } from "node:test";
import receiver, { handlePublicEvent, handlePublicEventReport } from "../src/index.js";

const secret="0123456789abcdef0123456789abcdef";
const nowMs=Date.parse("2026-10-07T12:00:00.000Z");
const timestamp=String(Math.floor(nowMs/1000));
const requestId="11111111-2222-4333-8444-555555555555";
const events=["lead_submit_ok","lead_submit_error","cal_click","telegram_click","whatsapp_click","line_click","email_click"];

function makeDb(rows=[]){
  const calls=[];
  return {
    calls,
    prepare(sql){
      const call={sql,bindings:null}; calls.push(call);
      return {
        bind(...args){ call.bindings=args; return { async run(){ return {meta:{changes:1}}; } }; },
        async all(){ return {results:rows}; },
      };
    },
  };
}
function limiter(success=true){ return { calls:[], async limit(arg){ this.calls.push(arg); return {success}; } }; }
function env(db=makeDb(),rate=limiter()){ return {LEAD_RECEIVER_ENABLED:"true",LEAD_WEBHOOK_SECRET:secret,DB:db,LEAD_RATE_LIMITER:rate}; }
function payload(event="cal_click"){
  return {schema:"ai-skill-lab.public-event.v1",requestId,occurredAt:"2026-10-07T12:00:00.000Z",event,page:"/pricing",locale:"en",ipToken:"a".repeat(64)};
}
function signedEvent(p=payload(), ts=timestamp){
  const raw=JSON.stringify(p);
  const digest=createHmac("sha256",secret).update("public-event-v1."+ts+"."+requestId+"."+raw).digest("hex");
  return new Request("https://worker.example/e3/event",{method:"POST",headers:{"Content-Type":"application/json","X-AI-Skill-Lab-Timestamp":ts,"X-AI-Skill-Lab-Request-Id":requestId,"X-AI-Skill-Lab-Public-Event-Signature":"v1="+digest},body:raw});
}
function signedReport(ts=timestamp){
  const digest=createHmac("sha256",secret).update("public-event-report-v1."+ts+"."+requestId).digest("hex");
  return new Request("https://worker.example/e3/event-report",{method:"GET",headers:{"X-AI-Skill-Lab-Timestamp":ts,"X-AI-Skill-Lab-Request-Id":requestId,"X-AI-Skill-Lab-Event-Report-Signature":"v1="+digest}});
}
async function json(r){ return JSON.parse(await r.text()); }

test("all seven events increment only aggregate day/event/page/locale counters",async()=>{
  for(const event of events){
    const db=makeDb(), rate=limiter(), e=env(db,rate);
    const r=await handlePublicEvent(signedEvent(payload(event)),e,nowMs);
    assert.equal(r.status,200,event);
    assert.deepEqual(await json(r),{ok:true});
    assert.equal(rate.calls.length,1);
    assert.deepEqual(rate.calls[0],{key:"event:"+"a".repeat(64)});
    assert.equal(db.calls.length,1);
    assert.match(db.calls[0].sql,/INSERT INTO public_event_daily_e38/);
    assert.deepEqual(db.calls[0].bindings,["2026-10-07",event,"/pricing","en"]);
    assert.equal(JSON.stringify(db.calls[0]).includes("a".repeat(64)),false);
  }
});

test("rejects tampering, invalid page and rate-limit overflow",async()=>{
  const bad={...payload(),page:"/pricing?q=x"};
  assert.equal((await handlePublicEvent(signedEvent(bad),env(),nowMs)).status,400);
  const req=signedEvent();
  req.headers.set("X-AI-Skill-Lab-Public-Event-Signature","v1="+"0".repeat(64));
  assert.equal((await handlePublicEvent(req,env(),nowMs)).status,401);
  assert.equal((await handlePublicEvent(signedEvent(),env(makeDb(),limiter(false)),nowMs)).status,429);
});

test("closed report requires HMAC and returns only aggregate rows",async()=>{
  const rows=[{day:"2026-10-07",event:"cal_click",page:"/pricing",locale:"en",count:3}];
  const e=env(makeDb(rows));
  assert.equal((await handlePublicEventReport(new Request("https://worker.example/e3/event-report"),e,nowMs)).status,401);
  const r=await handlePublicEventReport(signedReport(),e,nowMs);
  assert.equal(r.status,200);
  assert.deepEqual(await json(r),{ok:true,rows});
});

test("default worker router binds event and report paths",async()=>{
  const db=makeDb([{day:"2026-10-07",event:"email_click",page:"/start",locale:"ru",count:1}]);
  const e=env(db);
  const ts=String(Math.floor(Date.now()/1000));
  const livePayload={...payload(),occurredAt:new Date(Number(ts)*1000).toISOString()};
  assert.equal((await receiver.fetch(signedEvent(livePayload,ts),e,{})).status,200);
  assert.equal((await receiver.fetch(signedReport(ts),e,{})).status,200);
});
