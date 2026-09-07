import assert from "node:assert/strict";
import { createHmac, randomUUID } from "node:crypto";
import { test } from "node:test";
import { cleanupExpired, handleReceiver } from "../src/index.js";

const secret = "0123456789abcdef0123456789abcdef";
const nowMs = Date.parse("2026-09-07T09:00:00.000Z");
const timestamp = String(Math.floor(nowMs / 1000));

function makeDb({ changes = 1, fail = false } = {}) {
  const calls = [];
  const db = {
    calls,
    prepare(sql) {
      const call = { sql, bindings: [] };
      calls.push(call);
      return {
        bind(...bindings) {
          call.bindings = bindings;
          return this;
        },
        async run() {
          if (fail) throw new Error("db failure");
          return { meta: { changes } };
        },
      };
    },
  };
  return db;
}

function basePayload(requestId = randomUUID()) {
  return {
    schema: "ai-skill-lab.lead.v2",
    name: "Robert",
    audience: "adult",
    contact: "@BiTFormer",
    goal: "Build a useful workflow",
    program: "",
    locale: "en",
    privacyConsent: true,
    adultConfirmed: false,
    source: "ai-skill-lab",
    sourcePath: "/start",
    requestId,
    receivedAt: "2026-09-07T09:00:00.000Z",
  };
}

function signedRequest(payload, opts = {}) {
  const body = opts.body ?? JSON.stringify(payload);
  const requestId = opts.requestId ?? payload.requestId;
  const ts = opts.timestamp ?? timestamp;
  const digest = createHmac("sha256", opts.secret ?? secret).update(`${ts}.${requestId}.${body}`).digest("hex");
  return new Request("https://receiver.example/r101b/lead", {
    method: opts.method ?? "POST",
    headers: {
      "Content-Type": opts.contentType ?? "application/json",
      "X-AI-Skill-Lab-Timestamp": ts,
      "X-AI-Skill-Lab-Request-Id": requestId,
      "X-AI-Skill-Lab-Signature": opts.signature ?? `v1=${digest}`,
      ...(opts.headers || {}),
    },
    body: ["GET", "HEAD"].includes(opts.method) ? undefined : body,
  });
}

async function json(response) {
  return JSON.parse(await response.text());
}

function env(db = makeDb()) {
  return { LEAD_RECEIVER_ENABLED: "true", LEAD_WEBHOOK_SECRET: secret, DB: db };
}

test("disabled receiver is fail-closed 404", async () => {
  const response = await handleReceiver(signedRequest(basePayload()), {}, nowMs);
  assert.equal(response.status, 404);
});

test("enabled receiver without secret or D1 binding returns 503", async () => {
  const request = signedRequest(basePayload());
  assert.equal((await handleReceiver(request.clone(), { LEAD_RECEIVER_ENABLED: "true" }, nowMs)).status, 503);
  assert.equal((await handleReceiver(request.clone(), { LEAD_RECEIVER_ENABLED: "true", LEAD_WEBHOOK_SECRET: secret }, nowMs)).status, 503);
});

test("wrong path and non-POST are rejected", async () => {
  const payload = basePayload();
  const wrongPath = new Request("https://receiver.example/other", signedRequest(payload));
  assert.equal((await handleReceiver(wrongPath, env(), nowMs)).status, 404);
  const get = signedRequest(payload, { method: "GET" });
  const response = await handleReceiver(get, env(), nowMs);
  assert.equal(response.status, 405);
  assert.equal(response.headers.get("allow"), "POST");
});

test("rejects non-JSON and actual body over 20k", async () => {
  const payload = basePayload();
  assert.equal((await handleReceiver(signedRequest(payload, { contentType: "text/plain" }), env(), nowMs)).status, 415);
  const huge = { ...payload, goal: "x".repeat(21_000) };
  assert.equal((await handleReceiver(signedRequest(huge), env(), nowMs)).status, 413);
});

test("rejects malformed auth headers and timestamp outside replay window", async () => {
  const payload = basePayload();
  assert.equal((await handleReceiver(signedRequest(payload, { signature: "v1=bad" }), env(), nowMs)).status, 401);
  assert.equal((await handleReceiver(signedRequest(payload, { timestamp: String(Number(timestamp) - 301) }), env(), nowMs)).status, 401);
});

test("HMAC binds exact raw body bytes", async () => {
  const payload = basePayload();
  const compact = JSON.stringify(payload);
  const digest = createHmac("sha256", secret).update(`${timestamp}.${payload.requestId}.${compact}`).digest("hex");
  const spaced = JSON.stringify(payload, null, 2);
  const response = await handleReceiver(signedRequest(payload, { body: spaced, signature: `v1=${digest}` }), env(), nowMs);
  assert.equal(response.status, 401);
});

test("valid signed lead inserts exactly once with 30-day expiry", async () => {
  const db = makeDb();
  const payload = basePayload();
  const response = await handleReceiver(signedRequest(payload), env(db), nowMs);
  assert.equal(response.status, 200);
  assert.deepEqual(await json(response), { ok: true, requestId: payload.requestId });
  assert.equal(response.headers.get("cache-control"), "no-store, max-age=0");
  assert.equal(db.calls.length, 1);
  assert.match(db.calls[0].sql, /INSERT INTO lead_intake_r101b/);
  assert.match(db.calls[0].sql, /ON CONFLICT\(request_id\) DO NOTHING/);
  assert.equal(db.calls[0].bindings[0], payload.requestId);
  assert.equal(db.calls[0].bindings[1], payload.receivedAt);
  assert.equal(db.calls[0].bindings[2], "2026-10-07T09:00:00.000Z");
  assert.equal(db.calls[0].bindings[13], "/start");
});

test("duplicate request id returns 409 without a second operation", async () => {
  const db = makeDb({ changes: 0 });
  const payload = basePayload();
  const response = await handleReceiver(signedRequest(payload), env(db), nowMs);
  assert.equal(response.status, 409);
  assert.deepEqual(await json(response), { ok: false, error: "Duplicate request" });
  assert.equal(db.calls.length, 1);
});

test("invalid payload is rejected before D1 write", async () => {
  const db = makeDb();
  const payload = { ...basePayload(), privacyConsent: false };
  const response = await handleReceiver(signedRequest(payload), env(db), nowMs);
  assert.equal(response.status, 400);
  assert.equal(db.calls.length, 0);
});

test("kids programs require parent audience and adult confirmation", async () => {
  for (const payload of [
    { ...basePayload(), program: "kids-creator", audience: "adult", adultConfirmed: true },
    { ...basePayload(), program: "kids-creator", audience: "parent", adultConfirmed: false },
  ]) {
    const db = makeDb();
    assert.equal((await handleReceiver(signedRequest(payload), env(db), nowMs)).status, 400);
    assert.equal(db.calls.length, 0);
  }
});

test("D1 failure returns generic 503", async () => {
  const response = await handleReceiver(signedRequest(basePayload()), env(makeDb({ fail: true })), nowMs);
  assert.equal(response.status, 503);
  assert.deepEqual(await json(response), { ok: false, error: "Receiver unavailable" });
});

test("cleanup is disabled by default and deletes expired rows only when enabled", async () => {
  const disabledDb = makeDb();
  assert.deepEqual(await cleanupExpired({ DB: disabledDb }, nowMs), { skipped: true });
  assert.equal(disabledDb.calls.length, 0);

  const db = makeDb();
  await cleanupExpired({ LEAD_RECEIVER_ENABLED: "true", DB: db }, nowMs);
  assert.equal(db.calls.length, 1);
  assert.equal(db.calls[0].sql, "DELETE FROM lead_intake_r101b WHERE expires_at <= ?");
  assert.deepEqual(db.calls[0].bindings, ["2026-09-07T09:00:00.000Z"]);
});
