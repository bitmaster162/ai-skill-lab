import fs from "node:fs";
import { createHmac, timingSafeEqual } from "node:crypto";
import { handleLead } from "./lead.js";

const FACTS = JSON.parse(fs.readFileSync(new URL("../faq_facts.json", import.meta.url), "utf8"));
const MAX_UPDATE_BYTES = 20_000;
const MAX_MESSAGE_CHARS = 1_000;
const MIN_SECRET_BYTES = 32;
const EVENT_SCHEMA = "ai-skill-lab.telegram-faq-event.v1";
const LOG_FIELDS = new Set(["updateId", "status", "action"]);
const AUDIENCES = new Set(["adult", "parent", "teen", "business"]);
const LOCALES = new Set(["ru", "en"]);
const SECRET_PATTERNS = [
  /\bsk-[A-Za-z0-9_-]{8,}/i,
  /\bghp_[A-Za-z0-9]{8,}/i,
  /\bgithub_pat_[A-Za-z0-9_]{8,}/i,
  /\bxox[A-Za-z]-[A-Za-z0-9-]{8,}/i,
  /\bAKIA[A-Z0-9]{8,}/,
  /-----BEGIN [A-Z0-9 ]+-----/,
  /\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/,
  /\b[0-9a-f]{32,}\b/i,
];

function logBot(level, event, fields = {}) {
  const record = { schema: EVENT_SCHEMA, component: "telegram_faq", event };
  for (const [key, value] of Object.entries(fields)) {
    if (LOG_FIELDS.has(key) && value !== undefined) record[key] = value;
  }
  const writer = level === "error" ? console.error : level === "warn" ? console.warn : console.log;
  writer(record);
}

function json(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store, max-age=0",
      "X-Content-Type-Options": "nosniff",
      ...extraHeaders,
    },
  });
}

function parseHttpsUrl(value) {
  if (typeof value !== "string" || !value.trim()) return null;
  try {
    const url = new URL(value.trim());
    if (url.protocol !== "https:" || url.username || url.password || url.search || url.hash) return null;
    return url;
  } catch {
    return null;
  }
}

function derivedWebhookSecret(leadSecret) {
  return createHmac("sha256", leadSecret)
    .update("telegram-faq-webhook-v1")
    .digest("hex");
}

function config(env) {
  if (env.TELEGRAM_FAQ_ENABLED !== "true") return { enabled: false };
  const leadSecret = typeof env.LEAD_WEBHOOK_SECRET === "string" ? env.LEAD_WEBHOOK_SECRET : "";
  const relay = parseHttpsUrl(env.TELEGRAM_FAQ_RELAY_URL);
  const ready = relay
    && Buffer.byteLength(leadSecret, "utf8") >= MIN_SECRET_BYTES
    && env.LEAD_INGRESS_ENABLED === "true";
  return {
    enabled: true,
    ready: Boolean(ready),
    leadSecret,
    relay,
    webhookSecret: ready ? derivedWebhookSecret(leadSecret) : "",
  };
}

function equalSecret(actual, expected) {
  const a = Buffer.from(actual || "", "utf8");
  const b = Buffer.from(expected || "", "utf8");
  return a.length === b.length && a.length > 0 && timingSafeEqual(a, b);
}

function hasSecret(text) {
  return SECRET_PATTERNS.some((pattern) => pattern.test(text));
}

function localeFrom(message) {
  return String(message?.from?.language_code || "").toLowerCase().startsWith("ru") ? "ru" : "en";
}

function faqItems(locale) {
  return locale === "ru" ? FACTS.ru : FACTS.en;
}

function faqMenu(locale) {
  const title = locale === "ru" ? "FAQ AI Skill Lab:" : "AI Skill Lab FAQ:";
  return [title, ...faqItems(locale).map(([question], index) => `${index + 1}. ${question}`),
    locale === "ru" ? "Ответ: /faq 1 … /faq 11" : "Answer: /faq 1 … /faq 11"].join("\n");
}

function faqAnswer(locale, index) {
  const item = faqItems(locale)[index - 1];
  if (!item) return faqMenu(locale);
  return `${item[0]}\n\n${item[1]}`;
}

function normalizeWords(value) {
  return new Set(String(value).toLowerCase().match(/[\p{L}\p{N}]+/gu)?.filter((word) => word.length > 2) || []);
}

function bestFaq(locale, input) {
  const query = normalizeWords(input);
  let best = null;
  let bestScore = 0;
  for (const [question, answer] of faqItems(locale)) {
    const words = normalizeWords(`${question} ${answer}`);
    let score = 0;
    for (const word of query) if (words.has(word)) score += 1;
    if (score > bestScore) {
      bestScore = score;
      best = [question, answer];
    }
  }
  return bestScore >= 2 ? best : null;
}

function intro(locale) {
  if (locale === "ru") {
    return [
      "AI Skill Lab FAQ bot.",
      "Я отвечаю только по опубликованному FAQ, даю путь к бесплатному 15-минутному intro и могу отправить короткий brief в заявку после явного согласия.",
      "Команды: /faq · /book · /brief",
    ].join("\n");
  }
  return [
    "AI Skill Lab FAQ bot.",
    "I answer only from the published FAQ, provide the free 15-minute intro path, and can submit a short brief after explicit consent.",
    "Commands: /faq · /book · /brief",
  ].join("\n");
}

function booking(locale) {
  return locale === "ru"
    ? `Бесплатный звонок-знакомство · 15 минут: ${FACTS.booking_path}`
    : `Free 15-minute intro call: ${FACTS.booking_path}`;
}

function briefHelp(locale) {
  return locale === "ru"
    ? [
      "Короткий brief отправляется в действующий /api/lead только после явного CONSENT.",
      "Формат: /brief adult|parent|teen|business | ru|en | ваша цель (до 600 знаков) | CONSENT",
      "Для parent/teen добавьте в конец: | ADULT",
      `Правила конфиденциальности: ${FACTS.privacy_path}`,
    ].join("\n")
    : [
      "A short brief is submitted through the existing /api/lead only after explicit CONSENT.",
      "Format: /brief adult|parent|teen|business | ru|en | your goal (max 600 chars) | CONSENT",
      "For parent/teen add: | ADULT",
      `Privacy notice: ${FACTS.privacy_path}`,
    ].join("\n");
}

function parseBrief(text) {
  const parts = text.split("|").map((part) => part.trim());
  const first = parts.shift() || "";
  const command = first.match(/^\/brief\s+(adult|parent|teen|business)\s*$/i);
  if (!command || parts.length < 3 || parts.length > 4) return null;
  const audience = command[1].toLowerCase();
  const locale = (parts.shift() || "").toLowerCase();
  const goal = parts.shift() || "";
  const consent = (parts.shift() || "").toUpperCase();
  const adult = (parts.shift() || "").toUpperCase();
  if (!AUDIENCES.has(audience) || !LOCALES.has(locale) || !goal || goal.length > 600 || consent !== "CONSENT") return null;
  if ((audience === "parent" || audience === "teen") && adult !== "ADULT") return { needsAdult: true, locale };
  return { audience, locale, goal, adultConfirmation: adult === "ADULT" };
}

function deterministicUuid(secret, updateId) {
  const bytes = createHmac("sha256", secret).update(`telegram-update-v1:${updateId}`).digest().subarray(0, 16);
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = bytes.toString("hex");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

function telegramIpToken(secret, userId) {
  return createHmac("sha256", secret).update(`telegram-user-v1:${userId}`).digest("hex");
}

function displayName(message) {
  const value = [message?.from?.first_name, message?.from?.last_name].filter(Boolean).join(" ").trim();
  return (value || "Telegram user").slice(0, 80);
}

function contact(message) {
  const username = typeof message?.from?.username === "string" ? message.from.username.trim() : "";
  if (username) return `@${username}`.slice(0, 120);
  return `telegram:user:${message?.from?.id}`.slice(0, 120);
}

function relayRequestId(secret, updateId) {
  const bytes = createHmac("sha256", secret)
    .update(`telegram-reply-request-v1:${updateId}`)
    .digest()
    .subarray(0, 16);
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = bytes.toString("hex");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

async function sendMessage(cfg, updateId, chatId, text, fetchImpl) {
  const requestId = relayRequestId(cfg.leadSecret, updateId);
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const body = JSON.stringify({
    schema: "ai-skill-lab.telegram-faq-reply.v1",
    requestId,
    chatId: String(chatId),
    text,
    disableWebPagePreview: true,
  });
  const digest = createHmac("sha256", cfg.leadSecret)
    .update(`telegram-faq-reply-v1.${timestamp}.${requestId}.${body}`)
    .digest("hex");
  const response = await fetchImpl(cfg.relay, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-AI-Skill-Lab-Timestamp": timestamp,
      "X-AI-Skill-Lab-Request-Id": requestId,
      "X-AI-Skill-Lab-Telegram-Relay-Signature": `v1=${digest}`,
    },
    body,
    signal: AbortSignal.timeout(8_000),
  });
  return response.ok;
}

async function submitBrief(message, updateId, parsed, cfg, env, leadHandler) {
  const payload = {
    name: displayName(message),
    audience: parsed.audience,
    contact: contact(message),
    goal: parsed.goal,
    program: "",
    locale: parsed.locale,
    privacyConsent: "yes",
    adultConfirmation: parsed.adultConfirmation ? "yes" : "",
    website: "",
    sourcePath: "/telegram-faq",
  };
  const request = new Request("https://aiskillab.work/api/lead", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: "https://aiskillab.work",
    },
    body: JSON.stringify(payload),
  });
  return leadHandler(request, env, {
    requestId: deterministicUuid(cfg.leadSecret, updateId),
    ipToken: telegramIpToken(cfg.leadSecret, message.from.id),
    acceptDuplicate: true,
  });
}

export async function handleTelegramFaq(request, env = process.env, deps = {}) {
  if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "POST" });
  const cfg = config(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.ready) return json({ ok: false, error: "Bot unavailable" }, 503);
  if (!equalSecret(request.headers.get("x-telegram-bot-api-secret-token"), cfg.webhookSecret)) {
    return json({ ok: false, error: "Unauthorized" }, 403);
  }
  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > MAX_UPDATE_BYTES) return json({ ok: false, error: "Request too large" }, 413);
  const raw = Buffer.from(await request.arrayBuffer());
  if (raw.byteLength > MAX_UPDATE_BYTES) return json({ ok: false, error: "Request too large" }, 413);

  let update;
  try { update = JSON.parse(raw.toString("utf8")); } catch { return json({ ok: false, error: "Invalid update" }, 400); }
  const updateId = Number.isSafeInteger(update?.update_id) ? update.update_id : null;
  const message = update?.message;
  if (updateId === null || !message || message?.chat?.type !== "private" || typeof message?.from?.id !== "number") {
    return json({ ok: true });
  }
  const chatId = message.chat.id;
  const text = typeof message.text === "string" ? message.text.trim().slice(0, MAX_MESSAGE_CHARS + 1) : "";
  if (!text) return json({ ok: true });
  const locale = localeFrom(message);
  const fetchImpl = deps.fetchImpl || fetch;
  const leadHandler = deps.leadHandler || handleLead;

  let reply;
  let action = "faq";
  if (text.length > MAX_MESSAGE_CHARS) {
    action = "too_long";
    reply = locale === "ru" ? "Сообщение слишком длинное." : "Message is too long.";
  } else if (hasSecret(text)) {
    action = "secret_rejected";
    reply = locale === "ru"
      ? "Не отправляйте пароли, API keys, токены или другие секреты. Удалите секрет и повторите запрос."
      : "Do not send passwords, API keys, tokens or other secrets. Remove the secret and try again.";
  } else if (/^\/start\b/i.test(text)) {
    action = "start";
    reply = intro(locale);
  } else if (/^\/book\b/i.test(text)) {
    action = "book";
    reply = booking(locale);
  } else if (/^\/faq(?:\s+(\d{1,2}))?\s*$/i.test(text)) {
    action = "faq";
    const match = text.match(/^\/faq(?:\s+(\d{1,2}))?\s*$/i);
    reply = match?.[1] ? faqAnswer(locale, Number(match[1])) : faqMenu(locale);
  } else if (/^\/brief(?:\s|$)/i.test(text)) {
    action = "brief";
    if (text.trim().toLowerCase() === "/brief") {
      reply = briefHelp(locale);
    } else {
      const parsed = parseBrief(text);
      if (!parsed) {
        reply = briefHelp(locale);
      } else if (parsed.needsAdult) {
        reply = parsed.locale === "ru"
          ? "Для parent/teen нужен явный маркер ADULT в конце команды."
          : "For parent/teen, add the explicit ADULT marker at the end of the command.";
      } else if (hasSecret(parsed.goal)) {
        action = "secret_rejected";
        reply = parsed.locale === "ru"
          ? "В brief обнаружен похожий на секрет фрагмент. Удалите его и повторите."
          : "The brief contains text that looks like a secret. Remove it and try again.";
      } else {
        const leadResponse = await submitBrief(message, updateId, parsed, cfg, env, leadHandler);
        let result = {};
        try { result = await leadResponse.json(); } catch {}
        if (leadResponse.ok && result.ok) {
          reply = parsed.locale === "ru"
            ? "Brief отправлен. Мы свяжемся по Telegram-контакту из этого чата."
            : "Brief submitted. We will follow up using the Telegram contact from this chat.";
        } else {
          action = "brief_fail";
          reply = parsed.locale === "ru"
            ? "Сейчас brief не отправился. Используйте форму: https://aiskillab.work/start"
            : "The brief could not be submitted right now. Use the form: https://aiskillab.work/start";
        }
      }
    }
  } else {
    const match = bestFaq(locale, text);
    reply = match ? `${match[0]}\n\n${match[1]}` : intro(locale);
  }

  let sent = false;
  try { sent = await sendMessage(cfg, updateId, chatId, reply, fetchImpl); } catch { sent = false; }
  logBot(sent ? "info" : "error", sent ? "reply_sent" : "reply_failed", {
    updateId,
    status: sent ? 200 : 502,
    action,
  });
  return sent ? json({ ok: true }) : json({ ok: false, error: "Bot unavailable" }, 502);
}

const telegramFaqHandler = {
  fetch(request) {
    return handleTelegramFaq(request);
  },
};

export default telegramFaqHandler;
