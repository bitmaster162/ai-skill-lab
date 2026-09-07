import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import { afterEach, test } from "node:test";
import { handleLead } from "../api/lead.js";

const secret = "0123456789abcdef0123456789abcdef";
const baseEnv = {
  LEAD_INGRESS_ENABLED: "true",
  LEAD_ALLOWED_ORIGINS: "https://ai-skill-lab.vercel.app,https://aiskillab.work",
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
  return new Request("https://ingress.example.test/api/lead", {
    method: options.method ?? "POST",
    headers: {
      "Content-Type": options.contentType ?? "application/json",
      Origin: options.origin ?? "https://ai-skill-lab.vercel.app",
      ...(options.headers || {}),
    },
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
    { ...baseEnv, LEAD_ALLOWED_ORIGINS: "http://ai-skill-lab.vercel.app" },
    { ...baseEnv, LEAD_ALLOWED_ORIGINS: "https://ai-skill-lab.vercel.app/path" },
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

  const timestamp = calls[0].init.headers["X-AI-Skill-Lab-Timestamp"];
  const requestId = calls[0].init.headers["X-AI-Skill-Lab-Request-Id"];
  const expected = createHmac("sha256", secret)
    .update(`${timestamp}.${requestId}.${downstreamBody}`)
    .digest("hex");
  assert.equal(calls[0].init.headers["X-AI-Skill-Lab-Signature"], `v1=${expected}`);
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
