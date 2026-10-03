import assert from "node:assert/strict";
import { createHmac, randomUUID } from "node:crypto";
import { test } from "node:test";
import { cleanupRouteRateEvents, handleRouteRateLimit } from "../src/index.js";

const secret = "0123456789abcdef0123456789abcdef";
const nowMs = Date.parse("2026-10-02T16:00:00.000Z");
const timestamp = String(Math.floor(nowMs / 1000));
const ipToken = createHmac("sha256", secret).update("route-ip-v1:203.0.113.7").digest("hex");

function makeDb({ changes = 1, fail = false } = {}) {
  const calls = [];
  return {
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
}

function makeRateLimiter({ success = true, fail = false } = {}) {
  const calls = [];
  return {
    calls,
    async limit(input) {
      calls.push(input);
      if (fail) throw new Error("rate failure");
      return { success };
    },
  };
}

function env(db = makeDb(), rateLimiter = makeRateLimiter()) {
  return {
    ROUTE_RATE_LIMIT_ENABLED: "true",
    LEAD_WEBHOOK_SECRET: secret,
    DB: db,
    LEAD_RATE_LIMITER: rateLimiter,
  };
}

function payload(requestId = randomUUID(), changes = {}) {
  return {
    schema: "ai-skill-lab.route-rate.v1",
    requestId,
    ipToken,
    hourlyLimit: 5,
    dailyLimit: 77,
    ...changes,
  };
}

function signedRequest(data = payload(), opts = {}) {
  const body = opts.body ?? JSON.stringify(data);
  const requestId = opts.requestId ?? data.requestId;
  const ts = opts.timestamp ?? timestamp;
  const digest = createHmac("sha256", opts.secret ?? secret)
    .update(`route-rate-v1.${ts}.${requestId}.${body}`)
    .digest("hex");
  return new Request(opts.url ?? "https://receiver.example/r159/route-limit", {
    method: opts.method ?? "POST",
    headers: {
      "Content-Type": opts.contentType ?? "application/json",
      "X-AI-Skill-Lab-Timestamp": ts,
      "X-AI-Skill-Lab-Request-Id": requestId,
      "X-AI-Skill-Lab-Route-Signature": opts.signature ?? `v1=${digest}`,
    },
    body: ["GET", "HEAD"].includes(opts.method) ? undefined : body,
  });
}

async function body(response) {
  return JSON.parse(await response.text());
}

test("route rate endpoint is disabled and fail-closed by default", async () => {
  const response = await handleRouteRateLimit(signedRequest(), {}, nowMs);
  assert.equal(response.status, 404);
});

test("route rate endpoint requires secret, D1 and existing rate-limit binding", async () => {
  const request = signedRequest();
  assert.equal((await handleRouteRateLimit(request.clone(), { ROUTE_RATE_LIMIT_ENABLED: "true" }, nowMs)).status, 503);
  assert.equal((await handleRouteRateLimit(request.clone(), { ROUTE_RATE_LIMIT_ENABLED: "true", LEAD_WEBHOOK_SECRET: secret }, nowMs)).status, 503);
  assert.equal((await handleRouteRateLimit(request.clone(), { ROUTE_RATE_LIMIT_ENABLED: "true", LEAD_WEBHOOK_SECRET: secret, DB: makeDb() }, nowMs)).status, 503);
});

test("route rate endpoint enforces path, method and media type", async () => {
  assert.equal((await handleRouteRateLimit(signedRequest(payload(), { url: "https://receiver.example/other" }), env(), nowMs)).status, 404);
  const get = await handleRouteRateLimit(signedRequest(payload(), { method: "GET" }), env(), nowMs);
  assert.equal(get.status, 405);
  assert.equal(get.headers.get("allow"), "POST");
  assert.equal((await handleRouteRateLimit(signedRequest(payload(), { contentType: "text/plain" }), env(), nowMs)).status, 415);
});

test("route rate signature is domain-separated and replay-window bound", async () => {
  const data = payload();
  const wrong = createHmac("sha256", secret)
    .update(`${timestamp}.${data.requestId}.${JSON.stringify(data)}`)
    .digest("hex");
  assert.equal((await handleRouteRateLimit(signedRequest(data, { signature: `v1=${wrong}` }), env(), nowMs)).status, 401);
  assert.equal((await handleRouteRateLimit(signedRequest(data, { timestamp: String(Number(timestamp) - 301) }), env(), nowMs)).status, 401);
});

test("payload fixes hourly limit at five and requires explicit positive daily limit", async () => {
  for (const changes of [{ hourlyLimit: 6 }, { dailyLimit: 0 }, { dailyLimit: null }, { ipToken: "bad" }]) {
    const data = payload(randomUUID(), changes);
    assert.equal((await handleRouteRateLimit(signedRequest(data), env(), nowMs)).status, 400);
  }
});

test("allowed request uses coarse binding then one exact central D1 insert", async () => {
  const db = makeDb();
  const limiter = makeRateLimiter();
  const data = payload();
  const response = await handleRouteRateLimit(signedRequest(data), env(db, limiter), nowMs);
  assert.equal(response.status, 200);
  assert.deepEqual(await body(response), { ok: true, requestId: data.requestId });
  assert.deepEqual(limiter.calls, [{ key: `route:${ipToken}` }]);
  assert.equal(db.calls.length, 1);
  assert.match(db.calls[0].sql, /INSERT INTO route_rate_event_r159/);
  assert.match(db.calls[0].sql, /COUNT\(\*\).*ip_token/s);
  assert.match(db.calls[0].sql, /COUNT\(\*\).*occurred_at/s);
  assert.deepEqual(db.calls[0].bindings, [
    data.requestId,
    ipToken,
    Math.floor(nowMs / 1000),
    ipToken,
    Math.floor(nowMs / 1000) - 3600,
    5,
    Math.floor(nowMs / 1000) - 86400,
    77,
  ]);
});

test("coarse binding rejection returns 429 before D1", async () => {
  const db = makeDb();
  const limiter = makeRateLimiter({ success: false });
  const response = await handleRouteRateLimit(signedRequest(), env(db, limiter), nowMs);
  assert.equal(response.status, 429);
  assert.equal(response.headers.get("retry-after"), "60");
  assert.equal(db.calls.length, 0);
});

test("exact D1 rejection returns 429 with hourly retry horizon", async () => {
  const db = makeDb({ changes: 0 });
  const response = await handleRouteRateLimit(signedRequest(), env(db), nowMs);
  assert.equal(response.status, 429);
  assert.equal(response.headers.get("retry-after"), "3600");
  assert.deepEqual(await body(response), { ok: false, error: "Too many requests" });
});

test("binding or D1 failure returns 503", async () => {
  assert.equal((await handleRouteRateLimit(signedRequest(), env(makeDb(), makeRateLimiter({ fail: true })), nowMs)).status, 503);
  assert.equal((await handleRouteRateLimit(signedRequest(), env(makeDb({ fail: true })), nowMs)).status, 503);
});

test("rate events log only request correlation and status", async () => {
  const entries = [];
  const original = { log: console.log, warn: console.warn, error: console.error };
  for (const level of Object.keys(original)) console[level] = (...args) => entries.push({ level, args });
  try {
    const data = payload();
    const response = await handleRouteRateLimit(signedRequest(data), env(), nowMs);
    assert.equal(response.status, 200);
    const serialized = JSON.stringify(entries);
    assert.equal(serialized.includes(ipToken), false);
    assert.equal(serialized.includes(secret), false);
    assert.equal(serialized.includes("203.0.113.7"), false);
    assert.equal(serialized.includes(data.requestId), true);
  } finally {
    Object.assign(console, original);
  }
});

test("route-rate cleanup is disabled by default and deletes only older-than-24h events when enabled", async () => {
  const disabled = makeDb();
  assert.deepEqual(await cleanupRouteRateEvents({ DB: disabled }, nowMs), { skipped: true });
  assert.equal(disabled.calls.length, 0);

  const db = makeDb();
  await cleanupRouteRateEvents({ ROUTE_RATE_LIMIT_ENABLED: "true", DB: db }, nowMs);
  assert.equal(db.calls.length, 1);
  assert.equal(db.calls[0].sql, "DELETE FROM route_rate_event_r159 WHERE occurred_at < ?");
  assert.deepEqual(db.calls[0].bindings, [Math.floor(nowMs / 1000) - 86400]);
});
