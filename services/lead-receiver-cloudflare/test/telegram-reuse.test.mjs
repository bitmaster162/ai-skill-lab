import assert from "node:assert/strict";
import { createHmac, randomUUID } from "node:crypto";
import { afterEach, test } from "node:test";
import { ensureTelegramFaqWebhook, handleTelegramFaqReply } from "../src/index.js";

const sharedSecret = "0123456789abcdef0123456789abcdef";
const botToken = "1234567890:abcdefghijklmnopqrstuvwxyzABCDE";
const webhookUrl = "https://ingress.example.test/api/telegram-faq";
const relayUrl = "https://receiver.example.test/r163/telegram-faq/reply";
const nowMs = Date.parse("2026-10-03T14:30:00.000Z");
const timestamp = String(Math.floor(nowMs / 1000));

const baseEnv = {
  TELEGRAM_FAQ_REUSE_ENABLED: "true",
  TELEGRAM_FAQ_WEBHOOK_URL: webhookUrl,
  LEAD_WEBHOOK_SECRET: sharedSecret,
  LEAD_NOTIFY_BOT_TOKEN: botToken,
};

const realConsole = { log: console.log, warn: console.warn, error: console.error };
afterEach(() => Object.assign(console, realConsole));

function relayRequest(payload = {}, options = {}) {
  const requestId = options.requestId ?? randomUUID();
  const body = JSON.stringify({
    schema: "ai-skill-lab.telegram-faq-reply.v1",
    requestId,
    chatId: "932299051",
    text: "AI Skill Lab FAQ reply",
    disableWebPagePreview: true,
    ...payload,
  });
  const ts = options.timestamp ?? timestamp;
  const digest = createHmac("sha256", sharedSecret)
    .update(`telegram-faq-reply-v1.${ts}.${requestId}.${body}`)
    .digest("hex");
  return new Request(relayUrl, {
    method: options.method ?? "POST",
    headers: {
      "Content-Type": options.contentType ?? "application/json",
      "X-AI-Skill-Lab-Timestamp": ts,
      "X-AI-Skill-Lab-Request-Id": requestId,
      "X-AI-Skill-Lab-Telegram-Relay-Signature": options.signature ?? `v1=${digest}`,
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

test("Telegram FAQ reuse relay is fail-closed by default", async () => {
  const remote = captureFetch();
  const response = await handleTelegramFaqReply(
    relayRequest(),
    { ...baseEnv, TELEGRAM_FAQ_REUSE_ENABLED: "false" },
    nowMs,
    remote.fetchImpl,
  );
  assert.equal(response.status, 404);
  assert.equal(remote.calls.length, 0);
});

test("reuse relay requires the existing shared secret and existing notify bot token", async () => {
  for (const key of ["LEAD_WEBHOOK_SECRET", "LEAD_NOTIFY_BOT_TOKEN"]) {
    const remote = captureFetch();
    const response = await handleTelegramFaqReply(
      relayRequest(),
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
    relayRequest({}, { method: "GET" }),
    relayRequest({}, { contentType: "text/plain" }),
    relayRequest({}, { timestamp: String(Number(timestamp) - 1000) }),
    relayRequest({}, { signature: "v1=" + "0".repeat(64) }),
  ];
  const expected = [405, 415, 401, 401];
  for (let index = 0; index < cases.length; index += 1) {
    const remote = captureFetch();
    const response = await handleTelegramFaqReply(cases[index], baseEnv, nowMs, remote.fetchImpl);
    assert.equal(response.status, expected[index]);
    assert.equal(remote.calls.length, 0);
  }
});

test("valid signed relay sends one message with the existing notification bot", async () => {
  const remote = captureFetch();
  const requestId = "11111111-2222-4333-8444-555555555555";
  const response = await handleTelegramFaqReply(
    relayRequest({}, { requestId }),
    baseEnv,
    nowMs,
    remote.fetchImpl,
  );
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true, requestId });
  assert.equal(remote.calls.length, 1);
  assert.equal(remote.calls[0].url, `https://api.telegram.org/bot${botToken}/sendMessage`);
  assert.equal(remote.calls[0].body.chat_id, "932299051");
  assert.equal(remote.calls[0].body.text, "AI Skill Lab FAQ reply");
  assert.equal(remote.calls[0].body.disable_web_page_preview, true);
});

test("invalid relay payload is rejected before Telegram", async () => {
  for (const payload of [
    { schema: "wrong" },
    { chatId: "not-a-chat" },
    { text: "" },
    { text: "x".repeat(4097) },
    { disableWebPagePreview: false },
  ]) {
    const remote = captureFetch();
    const response = await handleTelegramFaqReply(relayRequest(payload), baseEnv, nowMs, remote.fetchImpl);
    assert.equal(response.status, 400);
    assert.equal(remote.calls.length, 0);
  }
});

test("Telegram relay provider failure is generic and custom logs contain metadata only", async () => {
  const entries = captureLogs();
  const remote = captureFetch([{ status: 500, body: { ok: false, description: "provider detail" } }]);
  const response = await handleTelegramFaqReply(relayRequest(), baseEnv, nowMs, remote.fetchImpl);
  assert.equal(response.status, 502);
  const raw = await response.text();
  assert.deepEqual(JSON.parse(raw), { ok: false, error: "Telegram relay unavailable" });
  const serialized = JSON.stringify(entries);
  for (const forbidden of [botToken, sharedSecret, "932299051", "AI Skill Lab FAQ reply", "provider detail"]) {
    assert.equal(serialized.includes(forbidden), false, forbidden);
  }
});

test("webhook sync is skipped while reuse is disabled", async () => {
  const remote = captureFetch();
  const result = await ensureTelegramFaqWebhook(
    { ...baseEnv, TELEGRAM_FAQ_REUSE_ENABLED: "false" },
    remote.fetchImpl,
  );
  assert.deepEqual(result, { skipped: true });
  assert.equal(remote.calls.length, 0);
});

test("webhook sync fails closed when token, shared secret or fixed webhook URL is missing", async () => {
  for (const key of ["LEAD_NOTIFY_BOT_TOKEN", "LEAD_WEBHOOK_SECRET", "TELEGRAM_FAQ_WEBHOOK_URL"]) {
    const remote = captureFetch();
    const result = await ensureTelegramFaqWebhook({ ...baseEnv, [key]: "" }, remote.fetchImpl);
    assert.deepEqual(result, { ok: false });
    assert.equal(remote.calls.length, 0, key);
  }
});

test("webhook sync makes no mutation when Telegram already points at the fixed FAQ URL", async () => {
  const remote = captureFetch([{ status: 200, body: { ok: true, result: { url: webhookUrl } } }]);
  const result = await ensureTelegramFaqWebhook(baseEnv, remote.fetchImpl);
  assert.deepEqual(result, { ok: true, changed: false });
  assert.equal(remote.calls.length, 1);
  assert.equal(remote.calls[0].url, `https://api.telegram.org/bot${botToken}/getWebhookInfo`);
  assert.equal(remote.calls[0].init.method, "GET");
});

test("webhook sync registers only the fixed configured URL with a derived secret token", async () => {
  const remote = captureFetch([
    { status: 200, body: { ok: true, result: { url: "" } } },
    { status: 200, body: { ok: true, result: true } },
  ]);
  const result = await ensureTelegramFaqWebhook(baseEnv, remote.fetchImpl);
  assert.deepEqual(result, { ok: true, changed: true });
  assert.equal(remote.calls.length, 2);
  assert.equal(remote.calls[1].url, `https://api.telegram.org/bot${botToken}/setWebhook`);
  assert.equal(remote.calls[1].init.method, "POST");
  assert.equal(remote.calls[1].body.url, webhookUrl);
  assert.equal(
    remote.calls[1].body.secret_token,
    createHmac("sha256", sharedSecret).update("telegram-faq-webhook-v1").digest("hex"),
  );
  assert.deepEqual(remote.calls[1].body.allowed_updates, ["message"]);
  assert.equal(remote.calls[1].body.drop_pending_updates, false);
});

test("webhook sync never logs bot token, shared secret or webhook URL", async () => {
  const entries = captureLogs();
  const remote = captureFetch([{ status: 500, body: { ok: false } }]);
  const result = await ensureTelegramFaqWebhook(baseEnv, remote.fetchImpl);
  assert.deepEqual(result, { ok: false });
  const serialized = JSON.stringify(entries);
  for (const forbidden of [botToken, sharedSecret, webhookUrl]) {
    assert.equal(serialized.includes(forbidden), false, forbidden);
  }
});
