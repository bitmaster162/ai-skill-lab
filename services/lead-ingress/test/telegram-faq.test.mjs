import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { handleTelegramFaq } from "../api/telegram-faq.js";

const botToken = "1234567890:abcdefghijklmnopqrstuvwxyzABCDE";
const webhookSecret = "telegram-webhook-secret-0123456789abcdef";
const leadSecret = "0123456789abcdef0123456789abcdef";
const baseEnv = {
  TELEGRAM_FAQ_ENABLED: "true",
  TELEGRAM_FAQ_BOT_TOKEN: botToken,
  TELEGRAM_FAQ_WEBHOOK_SECRET: webhookSecret,
  LEAD_INGRESS_ENABLED: "true",
  LEAD_WEBHOOK_SECRET: leadSecret,
};

const realConsole = { log: console.log, warn: console.warn, error: console.error };
afterEach(() => Object.assign(console, realConsole));

function update(text = "/start", options = {}) {
  return {
    update_id: options.updateId ?? 1001,
    message: {
      message_id: 7,
      text,
      chat: { id: options.chatId ?? 501, type: options.chatType ?? "private" },
      from: {
        id: options.userId ?? 701,
        first_name: options.firstName ?? "Robert",
        last_name: options.lastName ?? "D",
        username: options.username === undefined ? "bitmaster" : options.username,
        language_code: options.language ?? "en",
      },
    },
  };
}

function req(payload = update(), options = {}) {
  return new Request("https://ingress.example.test/api/telegram-faq", {
    method: options.method ?? "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Bot-Api-Secret-Token": options.secret ?? webhookSecret,
      ...(options.headers || {}),
    },
    body: options.method === "GET" ? undefined : (options.raw ?? JSON.stringify(payload)),
  });
}

function captureTelegram(status = 200) {
  const calls = [];
  const fetchImpl = async (url, init) => {
    calls.push({ url: String(url), init, body: JSON.parse(init.body) });
    return new Response(JSON.stringify({ ok: status >= 200 && status < 300 }), { status });
  };
  return { calls, fetchImpl };
}

function captureLead(status = 200, body = { ok: true, requestId: "00000000-0000-4000-8000-000000000001" }) {
  const calls = [];
  const leadHandler = async (request, env, internal) => {
    calls.push({
      request,
      env,
      internal,
      body: JSON.parse(await request.clone().text()),
    });
    return new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  };
  return { calls, leadHandler };
}

test("disabled bot is fail-closed 404", async () => {
  const tg = captureTelegram();
  const response = await handleTelegramFaq(req(), { ...baseEnv, TELEGRAM_FAQ_ENABLED: "false" }, { fetchImpl: tg.fetchImpl });
  assert.equal(response.status, 404);
  assert.equal(tg.calls.length, 0);
});

test("enabled bot requires token, webhook secret, lead secret and lead ingress", async () => {
  for (const key of ["TELEGRAM_FAQ_BOT_TOKEN", "TELEGRAM_FAQ_WEBHOOK_SECRET", "LEAD_WEBHOOK_SECRET", "LEAD_INGRESS_ENABLED"]) {
    const tg = captureTelegram();
    const env = { ...baseEnv, [key]: "" };
    const response = await handleTelegramFaq(req(), env, { fetchImpl: tg.fetchImpl });
    assert.equal(response.status, 503, key);
    assert.equal(tg.calls.length, 0, key);
  }
});

test("webhook requires POST and exact Telegram secret header", async () => {
  const tg = captureTelegram();
  const method = await handleTelegramFaq(req(update(), { method: "GET" }), baseEnv, { fetchImpl: tg.fetchImpl });
  assert.equal(method.status, 405);
  assert.equal(method.headers.get("allow"), "POST");
  const unauthorized = await handleTelegramFaq(req(update(), { secret: "wrong" }), baseEnv, { fetchImpl: tg.fetchImpl });
  assert.equal(unauthorized.status, 403);
  assert.equal(tg.calls.length, 0);
});

test("non-private or non-text updates are acknowledged without reply", async () => {
  const tg = captureTelegram();
  const group = await handleTelegramFaq(req(update("/start", { chatType: "group" })), baseEnv, { fetchImpl: tg.fetchImpl });
  assert.equal(group.status, 200);
  const noText = update();
  delete noText.message.text;
  const second = await handleTelegramFaq(req(noText), baseEnv, { fetchImpl: tg.fetchImpl });
  assert.equal(second.status, 200);
  assert.equal(tg.calls.length, 0);
});

test("/start, /book and /faq use bounded published paths and FAQ text", async () => {
  const tg = captureTelegram();
  for (const text of ["/start", "/book", "/faq 1"]) {
    const response = await handleTelegramFaq(req(update(text)), baseEnv, { fetchImpl: tg.fetchImpl });
    assert.equal(response.status, 200);
  }
  assert.equal(tg.calls.length, 3);
  assert.match(tg.calls[0].body.text, /FAQ bot/);
  assert.match(tg.calls[1].body.text, /https:\/\/aiskillab\.work\/start/);
  assert.match(tg.calls[2].body.text, /Is this a recorded course\?/);
  assert.match(tg.calls[2].body.text, /The core format is one-to-one/);
  assert.equal(tg.calls.every((call) => call.body.disable_web_page_preview === true), true);
});

test("free text selects FAQ deterministically and unknown text falls back to command help", async () => {
  const tg = captureTelegram();
  assert.equal((await handleTelegramFaq(req(update("How long is one session?")), baseEnv, { fetchImpl: tg.fetchImpl })).status, 200);
  assert.match(tg.calls[0].body.text, /One session is 60 minutes/);
  assert.equal((await handleTelegramFaq(req(update("xyzzy frobnicate")), baseEnv, { fetchImpl: tg.fetchImpl })).status, 200);
  assert.match(tg.calls[1].body.text, /Commands: \/faq/);
});

test("secret-like text is rejected before FAQ or lead handling", async () => {
  const tg = captureTelegram();
  const lead = captureLead();
  const response = await handleTelegramFaq(
    req(update("please check sk-proj-TESTSECRET123456")),
    baseEnv,
    { fetchImpl: tg.fetchImpl, leadHandler: lead.leadHandler },
  );
  assert.equal(response.status, 200);
  assert.equal(lead.calls.length, 0);
  assert.match(tg.calls[0].body.text, /Do not send passwords/);
});

test("/brief without exact consent only returns instructions", async () => {
  const tg = captureTelegram();
  const lead = captureLead();
  for (const text of ["/brief", "/brief adult | en | Build an agent", "/brief parent | en | Choose a program | CONSENT"]) {
    const response = await handleTelegramFaq(req(update(text)), baseEnv, { fetchImpl: tg.fetchImpl, leadHandler: lead.leadHandler });
    assert.equal(response.status, 200);
  }
  assert.equal(lead.calls.length, 0);
  assert.match(tg.calls[0].body.text, /explicit CONSENT/);
  assert.match(tg.calls[2].body.text, /ADULT/);
});

test("adult brief reuses the lead handler with explicit consent and deterministic privacy-safe identifiers", async () => {
  const tg = captureTelegram();
  const lead = captureLead();
  const payload = update("/brief adult | en | Build one useful AI workflow | CONSENT", { updateId: 424242, userId: 989898 });
  const response = await handleTelegramFaq(req(payload), baseEnv, { fetchImpl: tg.fetchImpl, leadHandler: lead.leadHandler });
  assert.equal(response.status, 200);
  assert.equal(lead.calls.length, 1);
  const call = lead.calls[0];
  assert.equal(call.body.name, "Robert D");
  assert.equal(call.body.contact, "@bitmaster");
  assert.equal(call.body.audience, "adult");
  assert.equal(call.body.locale, "en");
  assert.equal(call.body.goal, "Build one useful AI workflow");
  assert.equal(call.body.privacyConsent, "yes");
  assert.equal(call.body.sourcePath, "/telegram-faq");
  assert.match(call.internal.requestId, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
  assert.match(call.internal.ipToken, /^[0-9a-f]{64}$/);
  assert.equal(call.internal.acceptDuplicate, true);
  assert.equal(call.request.headers.get("origin"), "https://aiskillab.work");
  assert.match(tg.calls[0].body.text, /Brief submitted/);
});

test("same Telegram update and user produce the same requestId and rate token for retry idempotency", async () => {
  const firstTg = captureTelegram();
  const firstLead = captureLead();
  const payload = update("/brief adult | en | Build one useful AI workflow | CONSENT", { updateId: 515151, userId: 616161 });
  await handleTelegramFaq(req(payload), baseEnv, { fetchImpl: firstTg.fetchImpl, leadHandler: firstLead.leadHandler });
  const secondTg = captureTelegram();
  const secondLead = captureLead();
  await handleTelegramFaq(req(payload), baseEnv, { fetchImpl: secondTg.fetchImpl, leadHandler: secondLead.leadHandler });
  assert.equal(firstLead.calls[0].internal.requestId, secondLead.calls[0].internal.requestId);
  assert.equal(firstLead.calls[0].internal.ipToken, secondLead.calls[0].internal.ipToken);
});

test("parent and teen briefs require explicit ADULT and forward that confirmation", async () => {
  const tg = captureTelegram();
  const lead = captureLead();
  const response = await handleTelegramFaq(
    req(update("/brief parent | en | Find a safe learning route | CONSENT | ADULT")),
    baseEnv,
    { fetchImpl: tg.fetchImpl, leadHandler: lead.leadHandler },
  );
  assert.equal(response.status, 200);
  assert.equal(lead.calls.length, 1);
  assert.equal(lead.calls[0].body.adultConfirmation, "yes");
});

test("lead failure returns the public fallback path without leaking provider detail", async () => {
  const tg = captureTelegram();
  const lead = captureLead(503, { ok: false, error: "sensitive downstream detail" });
  const response = await handleTelegramFaq(
    req(update("/brief adult | en | Build a workflow | CONSENT")),
    baseEnv,
    { fetchImpl: tg.fetchImpl, leadHandler: lead.leadHandler },
  );
  assert.equal(response.status, 200);
  assert.match(tg.calls[0].body.text, /https:\/\/aiskillab\.work\/start/);
  assert.equal(tg.calls[0].body.text.includes("sensitive downstream detail"), false);
});

test("structured bot logs contain metadata only", async () => {
  const entries = [];
  console.log = (...args) => entries.push(args[0]);
  console.warn = (...args) => entries.push(args[0]);
  console.error = (...args) => entries.push(args[0]);
  const tg = captureTelegram();
  const secretQuestion = "How long is one session?";
  await handleTelegramFaq(req(update(secretQuestion, { username: "privatehandle" })), baseEnv, { fetchImpl: tg.fetchImpl });
  assert.equal(entries.length, 1);
  assert.deepEqual(Object.keys(entries[0]).sort(), ["action", "component", "event", "schema", "status", "updateId"].sort());
  const serialized = JSON.stringify(entries);
  for (const forbidden of [secretQuestion, "privatehandle", botToken, webhookSecret, leadSecret]) {
    assert.equal(serialized.includes(forbidden), false, forbidden);
  }
});

test("Telegram provider failure returns 502 without exposing bot token", async () => {
  const tg = captureTelegram(500);
  const response = await handleTelegramFaq(req(update("/start")), baseEnv, { fetchImpl: tg.fetchImpl });
  assert.equal(response.status, 502);
  const raw = await response.text();
  assert.deepEqual(JSON.parse(raw), { ok: false, error: "Bot unavailable" });
  assert.equal(raw.includes(botToken), false);
});
