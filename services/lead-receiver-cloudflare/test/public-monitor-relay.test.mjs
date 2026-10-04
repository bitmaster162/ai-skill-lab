import assert from "node:assert/strict";
import { createHmac, randomUUID } from "node:crypto";
import { afterEach, test } from "node:test";
import { handlePublicMonitorAlert } from "../src/index.js";

const relaySecret = "abcdef0123456789abcdef0123456789";
const botToken = "1234567890:abcdefghijklmnopqrstuvwxyzABCDE";
const chatId = "-1001234567890";
const relayUrl = "https://receiver.example.test/r164/public-monitor/alert";
const nowMs = Date.parse("2026-10-04T08:00:00.000Z");
const timestamp = String(Math.floor(nowMs / 1000));

const baseEnv = {
  PUBLIC_MONITOR_RELAY_ENABLED: "true",
  PUBLIC_MONITOR_RELAY_SECRET: relaySecret,
  LEAD_NOTIFY_BOT_TOKEN: botToken,
  LEAD_NOTIFY_CHAT_ID: chatId,
};

const realConsole = { log: console.log, warn: console.warn, error: console.error };
afterEach(() => Object.assign(console, realConsole));

function alertRequest(payload = {}, options = {}) {
  const requestId = options.requestId ?? randomUUID();
  const body = JSON.stringify({
    schema: "ai-skill-lab.public-monitor-alert.v1",
    requestId,
    failures: [
      {
        name: "bitevo-start",
        expected: 200,
        actual: 503,
        error: "unexpected_status=503",
      },
    ],
    ...payload,
  });
  const ts = options.timestamp ?? timestamp;
  const digest = createHmac("sha256", relaySecret)
    .update(`public-monitor-alert-v1.${ts}.${requestId}.${body}`)
    .digest("hex");

  return new Request(relayUrl, {
    method: options.method ?? "POST",
    headers: {
      "Content-Type": options.contentType ?? "application/json",
      "X-AI-Skill-Lab-Timestamp": ts,
      "X-AI-Skill-Lab-Request-Id": requestId,
      "X-AI-Skill-Lab-Public-Monitor-Signature": options.signature ?? `v1=${digest}`,
    },
    body: options.method === "GET" ? undefined : body,
  });
}

function captureFetch(responses = []) {
  const calls = [];
  const fetchImpl = async (url, init = {}) => {
    calls.push({ url: String(url), init, body: init.body ? JSON.parse(init.body) : null });
    const next = responses.shift() ?? { status: 200, body: { ok: true } };
    return new Response(JSON.stringify(next.body ?? { ok: true }), {
      status: next.status ?? 200,
      headers: { "Content-Type": "application/json" },
    });
  };
  return { calls, fetchImpl };
}

function captureLogs() {
  const entries = [];
  console.log = (...args) => entries.push(args[0]);
  console.warn = (...args) => entries.push(args[0]);
  console.error = (...args) => entries.push(args[0]);
  return entries;
}

test("public monitor relay is fail-closed by default", async () => {
  const remote = captureFetch();
  const response = await handlePublicMonitorAlert(
    alertRequest(),
    { ...baseEnv, PUBLIC_MONITOR_RELAY_ENABLED: "false" },
    nowMs,
    remote.fetchImpl,
  );
  assert.equal(response.status, 404);
  assert.equal(remote.calls.length, 0);
});

test("relay requires dedicated secret and existing owner Telegram bindings", async () => {
  for (const key of ["PUBLIC_MONITOR_RELAY_SECRET", "LEAD_NOTIFY_BOT_TOKEN", "LEAD_NOTIFY_CHAT_ID"]) {
    const remote = captureFetch();
    const response = await handlePublicMonitorAlert(
      alertRequest(),
      { ...baseEnv, [key]: "" },
      nowMs,
      remote.fetchImpl,
    );
    assert.equal(response.status, 503, key);
    assert.equal(remote.calls.length, 0, key);
  }
});

test("relay rejects wrong method, media type, stale timestamp and bad signature before Telegram", async () => {
  const cases = [
    alertRequest({}, { method: "GET" }),
    alertRequest({}, { contentType: "text/plain" }),
    alertRequest({}, { timestamp: String(Number(timestamp) - 1000) }),
    alertRequest({}, { signature: "v1=" + "0".repeat(64) }),
  ];
  const expected = [405, 415, 401, 401];
  for (let index = 0; index < cases.length; index += 1) {
    const remote = captureFetch();
    const response = await handlePublicMonitorAlert(cases[index], baseEnv, nowMs, remote.fetchImpl);
    assert.equal(response.status, expected[index]);
    assert.equal(remote.calls.length, 0);
  }
});

test("valid signed alert sends one bounded owner notification through existing bot", async () => {
  const remote = captureFetch();
  const requestId = "11111111-2222-4333-8444-555555555555";
  const response = await handlePublicMonitorAlert(
    alertRequest({}, { requestId }),
    baseEnv,
    nowMs,
    remote.fetchImpl,
  );

  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true, requestId });
  assert.equal(remote.calls.length, 1);
  assert.equal(remote.calls[0].url, `https://api.telegram.org/bot${botToken}/sendMessage`);
  assert.equal(remote.calls[0].body.chat_id, chatId);
  assert.equal(remote.calls[0].body.disable_web_page_preview, true);
  assert.equal(
    remote.calls[0].body.text,
    [
      "AI Skill Lab P27.7 public GET monitor failed.",
      "- bitevo-start: expected=200 observed=503 url=https://bitevo.work/start",
    ].join("\n"),
  );
});

test("relay rejects arbitrary or inconsistent failure metadata", async () => {
  const invalidPayloads = [
    { schema: "wrong" },
    { failures: [] },
    { failures: Array.from({ length: 6 }, (_, i) => ({
      name: i === 0 ? "bitevo-home" : "unknown-" + i,
      expected: 200,
      actual: 500,
      error: "unexpected_status=500",
    })) },
    { failures: [{ name: "unknown", expected: 200, actual: 500, error: "unexpected_status=500" }] },
    { failures: [{ name: "bitevo-home", expected: 201, actual: 500, error: "unexpected_status=500" }] },
    { failures: [{ name: "bitevo-home", expected: 200, actual: 500, error: "unexpected_status=404" }] },
    { failures: [{ name: "bitevo-home", expected: 200, actual: null, error: "private detail" }] },
    { failures: [
      { name: "bitevo-home", expected: 200, actual: 500, error: "unexpected_status=500" },
      { name: "bitevo-home", expected: 200, actual: 500, error: "unexpected_status=500" },
    ] },
  ];

  for (const payload of invalidPayloads) {
    const remote = captureFetch();
    const response = await handlePublicMonitorAlert(alertRequest(payload), baseEnv, nowMs, remote.fetchImpl);
    assert.equal(response.status, 400);
    assert.equal(remote.calls.length, 0);
  }
});

test("request-error alert allows only bounded error type and canonical target URL", async () => {
  const remote = captureFetch();
  const requestId = "11111111-2222-4333-8444-555555555555";
  const response = await handlePublicMonitorAlert(
    alertRequest({
      failures: [
        {
          name: "aiskillab-home",
          expected: 200,
          actual: null,
          error: "request_error=TimeoutError",
        },
      ],
    }, { requestId }),
    baseEnv,
    nowMs,
    remote.fetchImpl,
  );

  assert.equal(response.status, 200);
  assert.equal(remote.calls.length, 1);
  assert.match(remote.calls[0].body.text, /aiskillab-home/);
  assert.match(remote.calls[0].body.text, /request_error=TimeoutError/);
  assert.match(remote.calls[0].body.text, /https:\/\/aiskillab\.work\//);
});

test("provider failure is generic and custom logs contain metadata only", async () => {
  const entries = captureLogs();
  const remote = captureFetch([{ status: 500, body: { ok: false, description: "provider detail" } }]);
  const response = await handlePublicMonitorAlert(alertRequest(), baseEnv, nowMs, remote.fetchImpl);

  assert.equal(response.status, 502);
  assert.deepEqual(JSON.parse(await response.text()), { ok: false, error: "Monitor relay unavailable" });
  const serialized = JSON.stringify(entries);
  for (const forbidden of [relaySecret, botToken, chatId, "bitevo-start", "provider detail"]) {
    assert.equal(serialized.includes(forbidden), false, forbidden);
  }
});
