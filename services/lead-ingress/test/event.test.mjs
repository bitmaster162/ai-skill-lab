import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { afterEach, test } from "node:test";
import { handlePublicEvent } from "../api/event.js";

const secret = "0123456789abcdef0123456789abcdef";
const env = {
  LEAD_INGRESS_ENABLED: "true",
  LEAD_ALLOWED_ORIGINS: "https://aiskillab.work",
  LEAD_WEBHOOK_URL: "https://receiver.example.test/lead",
  LEAD_WEBHOOK_SECRET: secret,
  LEAD_RATE_LIMIT_READY: "true",
};
const events = ["lead_submit_ok","lead_submit_error","cal_click","telegram_click","whatsapp_click","line_click","email_click"];
const realFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = realFetch; });

function req(body={event:"cal_click",page:"/pricing",locale:"en"}, opts={}) {
  const headers = {
    "Content-Type": opts.contentType ?? "application/json",
    Origin: opts.origin ?? "https://aiskillab.work",
    "X-Forwarded-For": opts.forwardedFor ?? "203.0.113.10",
  };
  if (opts.forwardedFor === null) delete headers["X-Forwarded-For"];
  return new Request("https://ingress.example.test/api/event", {
    method: opts.method ?? "POST",
    headers,
    body: ["GET","HEAD"].includes(opts.method) ? undefined : (opts.raw ?? JSON.stringify(body)),
  });
}
async function body(r){ return JSON.parse(await r.text()); }
function capture(status=200){
  const calls=[];
  globalThis.fetch=async(url,init)=>{ calls.push({url:String(url),init}); return new Response("ok",{status}); };
  return calls;
}

test("accepts exactly seven event names and forwards no client fields beyond the event contract", async()=>{
  for(const event of events){
    const calls=capture();
    const response=await handlePublicEvent(req({event,page:"/start",locale:"ru"}),env);
    assert.equal(response.status,200,event);
    assert.deepEqual(await body(response),{ok:true});
    assert.equal(calls.length,1);
    assert.equal(calls[0].url,"https://receiver.example.test/e3/event");
    const payload=JSON.parse(calls[0].init.body);
    assert.deepEqual(Object.keys(payload).sort(),["event","ipToken","locale","occurredAt","page","requestId","schema"].sort());
    assert.equal(payload.event,event);
    assert.equal(payload.page,"/start");
    assert.equal(payload.locale,"ru");
    assert.equal(payload.schema,"ai-skill-lab.public-event.v1");
    assert.equal(calls[0].init.body.includes("203.0.113.10"),false);
  }
});

test("rejects form fields, cookies-as-data, unknown event, query/hash page and bad locale", async()=>{
  for(const input of [
    {event:"cal_click",page:"/pricing",locale:"en",name:"Robert"},
    {event:"cal_click",page:"/pricing",locale:"en",contact:"x"},
    {event:"cal_click",page:"/pricing",locale:"en",goal:"x"},
    {event:"cal_click",page:"/pricing",locale:"en",cookie:"x"},
    {event:"other",page:"/pricing",locale:"en"},
    {event:"cal_click",page:"/pricing?q=x",locale:"en"},
    {event:"cal_click",page:"/pricing#x",locale:"en"},
    {event:"cal_click",page:"/pricing",locale:"fr"},
  ]){
    const calls=capture();
    const response=await handlePublicEvent(req(input),env);
    assert.equal(response.status,400);
    assert.equal(calls.length,0);
  }
});

test("requires POST JSON canonical origin and client IP", async()=>{
  assert.equal((await handlePublicEvent(req(undefined,{method:"GET"}),env)).status,405);
  assert.equal((await handlePublicEvent(req(undefined,{contentType:"text/plain"}),env)).status,415);
  assert.equal((await handlePublicEvent(req(undefined,{origin:"https://evil.example"}),env)).status,403);
  assert.equal((await handlePublicEvent(req(undefined,{forwardedFor:null}),env)).status,503);
});

test("uses domain-separated HMAC IP token and exact signed body", async()=>{
  const calls=capture();
  const response=await handlePublicEvent(req(),env);
  assert.equal(response.status,200);
  const call=calls[0];
  const payload=JSON.parse(call.init.body);
  const expectedToken=createHmac("sha256",secret).update("public-event-ip-v1:203.0.113.10").digest("hex");
  assert.equal(payload.ipToken,expectedToken);
  const timestamp=call.init.headers["X-AI-Skill-Lab-Timestamp"];
  const requestId=call.init.headers["X-AI-Skill-Lab-Request-Id"];
  const expected=createHmac("sha256",secret).update(`public-event-v1.${timestamp}.${requestId}.${call.init.body}`).digest("hex");
  assert.equal(call.init.headers["X-AI-Skill-Lab-Public-Event-Signature"],`v1=${expected}`);
});

test("fails closed when disabled, incomplete, or downstream rejects", async()=>{
  assert.equal((await handlePublicEvent(req(),{...env,LEAD_INGRESS_ENABLED:"false"})).status,404);
  assert.equal((await handlePublicEvent(req(),{...env,LEAD_WEBHOOK_SECRET:"short"})).status,503);
  capture(500);
  assert.equal((await handlePublicEvent(req(),env)).status,502);
});
