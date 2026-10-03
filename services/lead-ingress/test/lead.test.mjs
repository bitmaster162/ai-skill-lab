import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { afterEach, test } from "node:test";
import { handleLead } from "../api/lead.js";

const secret = "0123456789abcdef0123456789abcdef";
const baseEnv = {
  LEAD_INGRESS_ENABLED: "true",
  LEAD_ALLOWED_ORIGINS: "https://aiskillab.work",
  LEAD_WEBHOOK_URL: "https://receiver.example.test/lead",
  LEAD_WEBHOOK_SECRET: secret,
  LEAD_LEGAL_OPERATOR_NAME: "Example Operator",
  LEAD_LEGAL_JURISDICTION: "Example Jurisdiction",
  LEAD_PRIVACY_CONTACT: "robert@aiskillab.work",
  LEAD_RETENTION_DAYS: "30",
  LEAD_RATE_LIMIT_READY: "true",
};

const valid = {
  name: "Robert",
  audience: "adult",
  contact: "@BiTFormer",
  goal: "Build a useful workflow",
  program: "",
  locale: "en",
  privacyConsent: "yes",
  adultConfirmation: "",
  website: "",
  sourcePath: "/start",
};

const realFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = realFetch;
});

function req(body = valid, options = {}) {
  const payload = options.raw ?? JSON.stringify(body);
  const headers = {
    "Content-Type": options.contentType ?? "application/json",
    Origin: options.origin ?? "https://aiskillab.work",
    ...(options.headers || {}),
  };
  if (options.forwardedFor !== null) {
    headers["X-Forwarded-For"] = options.forwardedFor ?? "203.0.113.10";
  }
  return new Request("https://ingress.example.test/api/lead", {
    method: options.method ?? "POST",
    headers,
    body: ["GET", "HEAD"].includes(options.method) ? undefined : payload,
  });
}

async function body(response) {
  return JSON.parse(await response.text());
}

function captureDownstream(status = 200) {
  const calls = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url: String(url), init });
    return new Response("ok", { status });
  };
  return calls;
}

function captureConsole() {
  const entries = [];
  const original = { log: console.log, warn: console.warn, error: console.error };
  for (const level of Object.keys(original)) console[level] = (...args) => entries.push({ level, args });
  return { entries, restore() { Object.assign(console, original); } };
}

test("disabled ingress returns 404 and never forwards", async () => {
  const calls = captureDownstream();
  const response = await handleLead(req(), { ...baseEnv, LEAD_INGRESS_ENABLED: "false" });
  assert.equal(response.status, 404);
  assert.equal(calls.length, 0);
});

test("non-POST methods return 405 with Allow", async () => {
  const response = await handleLead(req(valid, { method: "GET" }), baseEnv);
  assert.equal(response.status, 405);
  assert.equal(response.headers.get("allow"), "POST");
});

test("enabled ingress fails closed when required config is incomplete", async () => {
  for (const key of ["LEAD_ALLOWED_ORIGINS", "LEAD_WEBHOOK_URL", "LEAD_WEBHOOK_SECRET", "LEAD_LEGAL_OPERATOR_NAME", "LEAD_LEGAL_JURISDICTION", "LEAD_PRIVACY_CONTACT", "LEAD_RETENTION_DAYS", "LEAD_RATE_LIMIT_READY"]) {
    const env = { ...baseEnv, [key]: "" };
    const response = await handleLead(req(), env);
    assert.equal(response.status, 503, key);
  }
});

test("rejects weak secret, non-HTTPS webhook, and malformed allowed origins", async () => {
  for (const env of [
    { ...baseEnv, LEAD_WEBHOOK_SECRET: "short" },
    { ...baseEnv, LEAD_WEBHOOK_URL: "http://receiver.example.test/lead" },
    { ...baseEnv, LEAD_ALLOWED_ORIGINS: "http://aiskillab.work" },
    { ...baseEnv, LEAD_ALLOWED_ORIGINS: "https://aiskillab.work/path" },
  ]) {
    const response = await handleLead(req(), env);
    assert.equal(response.status, 503);
  }
});

test("rejects missing or disallowed Origin", async () => {
  const missing = new Request("https://ingress.example.test/api/lead", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(valid),
  });
  assert.equal((await handleLead(missing, baseEnv)).status, 403);
  assert.equal((await handleLead(req(valid, { origin: "https://evil.example" }), baseEnv)).status, 403);
});

test("rejects legacy redirect-only origin without forwarding", async () => {
  const calls = captureDownstream();
  const response = await handleLead(req(valid, { origin: "https://ai-skill-lab.vercel.app" }), baseEnv);
  assert.equal(response.status, 403);
  assert.equal(calls.length, 0);
});

test("rejects non-JSON content type", async () => {
  assert.equal((await handleLead(req(valid, { contentType: "text/plain" }), baseEnv)).status, 415);
});

test("enforces declared and actual 20k body limit", async () => {
  const declared = req(valid, { headers: { "Content-Length": "20001" } });
  assert.equal((await handleLead(declared, baseEnv)).status, 413);
  const huge = req(valid, { raw: JSON.stringify({ ...valid, goal: "x".repeat(21_000) }) });
  assert.equal((await handleLead(huge, baseEnv)).status, 413);
});

test("rejects invalid JSON", async () => {
  assert.equal((await handleLead(req(valid, { raw: "{" }), baseEnv)).status, 400);
});

test("honeypot succeeds without forwarding", async () => {
  const calls = captureDownstream();
  const response = await handleLead(req({ ...valid, website: "bot.example" }), baseEnv);
  assert.equal(response.status, 200);
  assert.deepEqual(await body(response), { ok: true });
  assert.equal(calls.length, 0);
});

test("requires exact audience and locale instead of silently defaulting", async () => {
  assert.equal((await handleLead(req({ ...valid, audience: "unknown" }), baseEnv)).status, 400);
  assert.equal((await handleLead(req({ ...valid, locale: "fr" }), baseEnv)).status, 400);
});

test("requires privacy consent", async () => {
  assert.equal((await handleLead(req({ ...valid, privacyConsent: "" }), baseEnv)).status, 400);
});

test("requires adult confirmation for parent, teen, and youth programs", async () => {
  for (const input of [
    { ...valid, audience: "parent" },
    { ...valid, audience: "teen" },
    { ...valid, program: "teens-builder" },
  ]) {
    assert.equal((await handleLead(req(input), baseEnv)).status, 400);
  }
});

test("kids programs require parent audience and adult confirmation", async () => {
  const wrongAudience = { ...valid, program: "kids-creator", audience: "adult", adultConfirmation: "yes" };
  assert.equal((await handleLead(req(wrongAudience), baseEnv)).status, 400);
  const good = { ...valid, program: "kids-creator", audience: "parent", adultConfirmation: "yes" };
  const calls = captureDownstream();
  assert.equal((await handleLead(req(good), baseEnv)).status, 200);
  assert.equal(calls.length, 1);
});

test("rejects missing required fields, non-string fields, overlong fields, and unsafe sourcePath", async () => {
  const cases = [
    { ...valid, name: "" },
    { ...valid, contact: "" },
    { ...valid, goal: { nested: true } },
    { ...valid, name: "x".repeat(81) },
    { ...valid, sourcePath: "https://evil.example" },
    { ...valid, sourcePath: "//evil.example" },
  ];
  for (const input of cases) assert.equal((await handleLead(req(input), baseEnv)).status, 400);
});

test("fails closed before forwarding when client IP is missing or invalid", async () => {
  for (const forwardedFor of [null, "not-an-ip"]) {
    const calls = captureDownstream();
    const response = await handleLead(req(valid, { forwardedFor }), baseEnv);
    assert.equal(response.status, 503);
    assert.deepEqual(await body(response), { ok: false, error: "Application channel unavailable" });
    assert.equal(calls.length, 0);
  }
});

test("derives a deterministic privacy-safe per-IP token and never forwards raw IP", async () => {
  const calls = captureDownstream();
  const firstIp = "203.0.113.10";
  const secondIp = "203.0.113.11";
  assert.equal((await handleLead(req(valid, { forwardedFor: firstIp }), baseEnv)).status, 200);
  assert.equal((await handleLead(req(valid, { forwardedFor: secondIp }), baseEnv)).status, 200);
  assert.equal(calls.length, 2);

  const first = JSON.parse(calls[0].init.body);
  const second = JSON.parse(calls[1].init.body);
  const expectedFirst = createHmac("sha256", secret).update(`lead-ip-v1:${firstIp}`).digest("hex");
  const expectedSecond = createHmac("sha256", secret).update(`lead-ip-v1:${secondIp}`).digest("hex");
  assert.equal(first.ipToken, expectedFirst);
  assert.equal(second.ipToken, expectedSecond);
  assert.notEqual(first.ipToken, second.ipToken);
  assert.equal(calls[0].init.body.includes(firstIp), false);
  assert.equal(calls[1].init.body.includes(secondIp), false);
});

test("success signs exact raw downstream body and returns request id", async () => {
  const calls = captureDownstream();
  const response = await handleLead(req(valid), baseEnv);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("cache-control"), "no-store, max-age=0");
  const result = await body(response);
  assert.equal(result.ok, true);
  assert.match(result.requestId, /^[0-9a-f-]{36}$/i);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, baseEnv.LEAD_WEBHOOK_URL);

  const downstreamBody = calls[0].init.body;
  const payload = JSON.parse(downstreamBody);
  assert.equal(payload.schema, "ai-skill-lab.lead.v2");
  assert.equal(payload.requestId, result.requestId);
  assert.equal(payload.sourcePath, "/start");
  assert.equal(payload.receivedAt.endsWith("Z"), true);
  const expectedIpToken = createHmac("sha256", secret)
    .update("lead-ip-v1:203.0.113.10")
    .digest("hex");
  assert.equal(payload.ipToken, expectedIpToken);
  assert.equal(downstreamBody.includes("203.0.113.10"), false);

  const timestamp = calls[0].init.headers["X-AI-Skill-Lab-Timestamp"];
  const requestId = calls[0].init.headers["X-AI-Skill-Lab-Request-Id"];
  const expected = createHmac("sha256", secret)
    .update(`${timestamp}.${requestId}.${downstreamBody}`)
    .digest("hex");
  assert.equal(calls[0].init.headers["X-AI-Skill-Lab-Signature"], `v1=${expected}`);
});

test("structured ingress events correlate outcomes without lead data or secrets", async () => {
  const audit = captureConsole();
  try {
    captureDownstream();
    const response = await handleLead(req(valid), baseEnv);
    const result = await body(response);
    const records = audit.entries.map((entry) => entry.args[0]);
    assert.deepEqual(records.map((record) => record.event), ["forward_start", "forward_ok"]);
    assert.equal(records[0].requestId, result.requestId);
    assert.equal(records[1].requestId, result.requestId);
    assert.deepEqual(Object.keys(records[1]).sort(), ["component", "downstreamStatus", "event", "requestId", "schema", "status"].sort());
    const serialized = JSON.stringify(records);
    const ipToken = createHmac("sha256", secret)
      .update("lead-ip-v1:203.0.113.10")
      .digest("hex");
    for (const forbidden of [valid.name, valid.contact, valid.goal, baseEnv.LEAD_WEBHOOK_URL, secret, "https://aiskillab.work", "203.0.113.10", ipToken]) {
      assert.equal(serialized.includes(forbidden), false, forbidden);
    }
  } finally {
    audit.restore();
  }
});

test("downstream rejection logs status only and still returns generic 502", async () => {
  const audit = captureConsole();
  try {
    captureDownstream(500);
    const response = await handleLead(req(valid), baseEnv);
    assert.equal(response.status, 502);
    const rejected = audit.entries.map((entry) => entry.args[0]).find((record) => record.event === "downstream_rejected");
    assert.equal(rejected.status, 502);
    assert.equal(rejected.downstreamStatus, 500);
  } finally {
    audit.restore();
  }
});

test("downstream non-2xx returns generic 502", async () => {
  captureDownstream(500);
  const response = await handleLead(req(valid), baseEnv);
  assert.equal(response.status, 502);
  assert.deepEqual(await body(response), { ok: false, error: "Application channel unavailable" });
});

test("downstream network error returns generic 502", async () => {
  globalThis.fetch = async () => { throw new Error("sensitive provider detail"); };
  const response = await handleLead(req(valid), baseEnv);
  assert.equal(response.status, 502);
  assert.deepEqual(await body(response), { ok: false, error: "Application channel unavailable" });
});

test("trusted internal options can supply deterministic request id and privacy-safe token without client IP", async () => {
  const calls = captureDownstream();
  const requestId = "11111111-2222-4333-8444-555555555555";
  const ipToken = "a".repeat(64);
  const response = await handleLead(req(valid, { forwardedFor: null }), baseEnv, { requestId, ipToken, acceptDuplicate: true });
  assert.equal(response.status, 200);
  const result = await body(response);
  assert.equal(result.requestId, requestId);
  assert.equal(calls.length, 1);
  const payload = JSON.parse(calls[0].init.body);
  assert.equal(payload.requestId, requestId);
  assert.equal(payload.ipToken, ipToken);
});

test("trusted internal options reject malformed request id or token before forwarding", async () => {
  for (const internal of [
    { requestId: "not-a-uuid", ipToken: "a".repeat(64) },
    { requestId: "11111111-2222-4333-8444-555555555555", ipToken: "bad" },
  ]) {
    const calls = captureDownstream();
    const response = await handleLead(req(valid, { forwardedFor: null }), baseEnv, internal);
    assert.equal(response.status, 503);
    assert.equal(calls.length, 0);
  }
});

test("trusted idempotent replay treats receiver duplicate as accepted while public duplicate stays generic", async () => {
  const requestId = "11111111-2222-4333-8444-555555555555";
  const ipToken = "b".repeat(64);
  captureDownstream(409);
  const trusted = await handleLead(req(valid, { forwardedFor: null }), baseEnv, { requestId, ipToken, acceptDuplicate: true });
  assert.equal(trusted.status, 200);
  assert.deepEqual(await body(trusted), { ok: true, requestId, duplicate: true });

  captureDownstream(409);
  const publicResponse = await handleLead(req(valid), baseEnv);
  assert.equal(publicResponse.status, 502);
  assert.deepEqual(await body(publicResponse), { ok: false, error: "Application channel unavailable" });
});
