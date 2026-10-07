const MAX_BODY_BYTES = 20_000;
const MIN_SECRET_BYTES = 32;
const MAX_SKEW_SECONDS = 300;
const RETENTION_DAYS = 30;
const ROUTE_RATE_PATH = "/r159/route-limit";
const ROUTE_RATE_SCHEMA = "ai-skill-lab.route-rate.v1";
const ROUTE_RATE_BODY_BYTES = 2_000;
const ROUTE_HOURLY_LIMIT = 5;
const ROUTE_WINDOW_SECONDS = 3_600;
const ROUTE_DAY_SECONDS = 86_400;
const NOTIFY_TIMEOUT_MS = 5_000;
const TELEGRAM_FAQ_REPLY_PATH = "/r163/telegram-faq/reply";
const TELEGRAM_FAQ_REPLY_SCHEMA = "ai-skill-lab.telegram-faq-reply.v1";
const TELEGRAM_FAQ_REPLY_BODY_BYTES = 8_000;
const TELEGRAM_MESSAGE_MAX_CHARS = 4_096;
const TELEGRAM_WEBHOOK_SECRET_DOMAIN = "telegram-faq-webhook-v1";
const TELEGRAM_REPLY_SIGNATURE_DOMAIN = "telegram-faq-reply-v1";
const PUBLIC_EVENT_PATH = "/e3/event";
const PUBLIC_EVENT_REPORT_PATH = "/e3/event-report";
const PUBLIC_EVENT_SCHEMA = "ai-skill-lab.public-event.v1";
const PUBLIC_EVENT_SIGNATURE_DOMAIN = "public-event-v1";
const PUBLIC_EVENT_REPORT_SIGNATURE_DOMAIN = "public-event-report-v1";
const PUBLIC_EVENT_BODY_BYTES = 2_000;
const PUBLIC_EVENT_NAMES = new Set([
  "lead_submit_ok",
  "lead_submit_error",
  "cal_click",
  "telegram_click",
  "whatsapp_click",
  "line_click",
  "email_click",
]);
const PUBLIC_EVENT_UPSERT_SQL = `
  INSERT INTO public_event_daily_e38 (day, event_name, page, locale, count)
  VALUES (?, ?, ?, ?, 1)
  ON CONFLICT(day, event_name, page, locale)
  DO UPDATE SET count = count + 1
`;
const PUBLIC_EVENT_REPORT_SQL = `
  SELECT day, event_name AS event, page, locale, count
  FROM public_event_daily_e38
  ORDER BY day DESC, event_name ASC, page ASC, locale ASC
  LIMIT 5000
`;
const PUBLIC_MONITOR_ALERT_PATH = "/r164/public-monitor/alert";
const PUBLIC_MONITOR_ALERT_SCHEMA = "ai-skill-lab.public-monitor-alert.v1";
const PUBLIC_MONITOR_ALERT_BODY_BYTES = 4_000;
const PUBLIC_MONITOR_SIGNATURE_DOMAIN = "public-monitor-alert-v1";
const PUBLIC_MONITOR_TARGET_URLS = Object.freeze({
  "bitevo-home": "https://bitevo.work/",
  "bitevo-pricing": "https://bitevo.work/pricing",
  "bitevo-start": "https://bitevo.work/start",
  "aiskillab-home": "https://aiskillab.work/",
  "aiskillab-start": "https://aiskillab.work/start",
});
const ALLOWED_AUDIENCES = new Set(["adult", "parent", "teen", "business"]);
const ALLOWED_LOCALES = new Set(["ru", "en"]);
const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SIGNATURE_V1 = /^v1=([0-9a-f]{64})$/;
const INTAKE_EVENT_SCHEMA = "ai-skill-lab.intake-event.v1";
const RECEIVER_EVENT_FIELDS = new Set(["requestId", "status", "deleted"]);
const ROUTE_RATE_INSERT_SQL = `
  INSERT INTO route_rate_event_r159 (request_id, ip_token, occurred_at)
  SELECT ?, ?, ?
  WHERE
    (SELECT COUNT(*) FROM route_rate_event_r159 WHERE ip_token = ? AND occurred_at >= ?) < ?
    AND
    (SELECT COUNT(*) FROM route_rate_event_r159 WHERE occurred_at >= ?) < ?
  ON CONFLICT(request_id) DO NOTHING
`;

function logReceiver(level, event, fields = {}) {
  const record = { schema: INTAKE_EVENT_SCHEMA, component: "receiver", event };
  for (const [key, value] of Object.entries(fields)) {
    if (RECEIVER_EVENT_FIELDS.has(key) && value !== undefined) record[key] = value;
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

function utf8Bytes(value) {
  return new TextEncoder().encode(value).byteLength;
}

function validText(value, max, { required = false } = {}) {
  if (value === undefined && !required) return true;
  if (typeof value !== "string") return false;
  if (required && !value) return false;
  return utf8Bytes(value) <= max;
}

function timingSafeHexEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i += 1) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

async function hmacHex(secret, value) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(value));
  return Array.from(new Uint8Array(signature), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function config(env) {
  if (env?.LEAD_RECEIVER_ENABLED !== "true") return { enabled: false };
  const secret = typeof env?.LEAD_WEBHOOK_SECRET === "string" ? env.LEAD_WEBHOOK_SECRET : "";
  const db = env?.DB;
  const rateLimiter = env?.LEAD_RATE_LIMITER;
  const ready = utf8Bytes(secret) >= MIN_SECRET_BYTES
    && db && typeof db.prepare === "function"
    && rateLimiter && typeof rateLimiter.limit === "function";
  return { enabled: true, ready, secret, db, rateLimiter };
}

function routeRateConfig(env) {
  if (env?.ROUTE_RATE_LIMIT_ENABLED !== "true") return { enabled: false };
  const secret = typeof env?.LEAD_WEBHOOK_SECRET === "string" ? env.LEAD_WEBHOOK_SECRET : "";
  const db = env?.DB;
  const rateLimiter = env?.LEAD_RATE_LIMITER;
  const ready = utf8Bytes(secret) >= MIN_SECRET_BYTES
    && db && typeof db.prepare === "function"
    && rateLimiter && typeof rateLimiter.limit === "function";
  return { enabled: true, ready, secret, db, rateLimiter };
}


function publicEventConfig(env) {
  if (env?.LEAD_RECEIVER_ENABLED !== "true") return { enabled: false };
  const secret = typeof env?.LEAD_WEBHOOK_SECRET === "string" ? env.LEAD_WEBHOOK_SECRET : "";
  const db = env?.DB;
  const rateLimiter = env?.LEAD_RATE_LIMITER;
  return {
    enabled: true,
    ready: utf8Bytes(secret) >= MIN_SECRET_BYTES
      && db && typeof db.prepare === "function"
      && rateLimiter && typeof rateLimiter.limit === "function",
    reportReady: utf8Bytes(secret) >= MIN_SECRET_BYTES
      && db && typeof db.prepare === "function",
    secret, db, rateLimiter,
  };
}

function validatePublicEventPayload(payload, requestId, timestampSeconds) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  if (payload.schema !== PUBLIC_EVENT_SCHEMA) return null;
  if (payload.requestId !== requestId || !UUID_V4.test(payload.requestId)) return null;
  if (!PUBLIC_EVENT_NAMES.has(payload.event)) return null;
  if (!ALLOWED_LOCALES.has(payload.locale)) return null;
  if (!validText(payload.page, 180, { required: true })) return null;
  if (!payload.page.startsWith("/") || payload.page.startsWith("//") || payload.page.includes("?") || payload.page.includes("#")) return null;
  if (typeof payload.ipToken !== "string" || !/^[0-9a-f]{64}$/.test(payload.ipToken)) return null;
  if (typeof payload.occurredAt !== "string") return null;
  const occurredMs = Date.parse(payload.occurredAt);
  if (!Number.isFinite(occurredMs) || new Date(occurredMs).toISOString() !== payload.occurredAt) return null;
  if (Math.abs(occurredMs - timestampSeconds * 1000) > MAX_SKEW_SECONDS * 1000) return null;
  return { requestId: payload.requestId, occurredAt: payload.occurredAt, event: payload.event, page: payload.page, locale: payload.locale, ipToken: payload.ipToken };
}

export async function handlePublicEvent(request, env = {}, nowMs = Date.now()) {
  const cfg = publicEventConfig(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.ready) return json({ ok: false, error: "Event counter unavailable" }, 503);
  const url = new URL(request.url);
  if (url.pathname !== PUBLIC_EVENT_PATH) return json({ ok: false, error: "Not found" }, 404);
  if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "POST" });
  if (!/^application\/json(?:\s*;|$)/i.test(request.headers.get("content-type") || "")) return json({ ok: false, error: "Unsupported media type" }, 415);
  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > PUBLIC_EVENT_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);
  const timestampRaw = request.headers.get("x-ai-skill-lab-timestamp") || "";
  const requestId = request.headers.get("x-ai-skill-lab-request-id") || "";
  const signatureRaw = request.headers.get("x-ai-skill-lab-public-event-signature") || "";
  const signatureMatch = SIGNATURE_V1.exec(signatureRaw);
  if (!/^[0-9]{10}$/.test(timestampRaw) || !UUID_V4.test(requestId) || !signatureMatch) return json({ ok: false, error: "Unauthorized" }, 401);
  const timestampSeconds = Number(timestampRaw);
  if (!Number.isSafeInteger(timestampSeconds) || Math.abs(Math.floor(nowMs / 1000) - timestampSeconds) > MAX_SKEW_SECONDS) return json({ ok: false, error: "Unauthorized" }, 401);
  const rawBytes = new Uint8Array(await request.arrayBuffer());
  if (rawBytes.byteLength > PUBLIC_EVENT_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);
  let rawBody;
  try { rawBody = new TextDecoder("utf-8", { fatal: true }).decode(rawBytes); } catch { return json({ ok: false, error: "Invalid data" }, 400); }
  const expectedDigest = await hmacHex(cfg.secret, `${PUBLIC_EVENT_SIGNATURE_DOMAIN}.${timestampRaw}.${requestId}.${rawBody}`);
  if (!timingSafeHexEqual(expectedDigest, signatureMatch[1])) return json({ ok: false, error: "Unauthorized" }, 401);
  let payload;
  try { payload = JSON.parse(rawBody); } catch { return json({ ok: false, error: "Invalid data" }, 400); }
  const row = validatePublicEventPayload(payload, requestId, timestampSeconds);
  if (!row) return json({ ok: false, error: "Invalid event" }, 400);
  try {
    const limitResult = await cfg.rateLimiter.limit({ key: `event:${row.ipToken}` });
    if (!limitResult?.success) return json({ ok: false, error: "Too many requests" }, 429, { "Retry-After": "60" });
  } catch { return json({ ok: false, error: "Event counter unavailable" }, 503); }
  try {
    await cfg.db.prepare(PUBLIC_EVENT_UPSERT_SQL).bind(row.occurredAt.slice(0, 10), row.event, row.page, row.locale).run();
  } catch { return json({ ok: false, error: "Event counter unavailable" }, 503); }
  return json({ ok: true });
}

export async function handlePublicEventReport(request, env = {}, nowMs = Date.now()) {
  const cfg = publicEventConfig(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.reportReady) return json({ ok: false, error: "Report unavailable" }, 503);
  const url = new URL(request.url);
  if (url.pathname !== PUBLIC_EVENT_REPORT_PATH) return json({ ok: false, error: "Not found" }, 404);
  if (request.method !== "GET") return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "GET" });
  const timestampRaw = request.headers.get("x-ai-skill-lab-timestamp") || "";
  const requestId = request.headers.get("x-ai-skill-lab-request-id") || "";
  const signatureRaw = request.headers.get("x-ai-skill-lab-event-report-signature") || "";
  const signatureMatch = SIGNATURE_V1.exec(signatureRaw);
  if (!/^[0-9]{10}$/.test(timestampRaw) || !UUID_V4.test(requestId) || !signatureMatch) return json({ ok: false, error: "Unauthorized" }, 401);
  const timestampSeconds = Number(timestampRaw);
  if (!Number.isSafeInteger(timestampSeconds) || Math.abs(Math.floor(nowMs / 1000) - timestampSeconds) > MAX_SKEW_SECONDS) return json({ ok: false, error: "Unauthorized" }, 401);
  const expectedDigest = await hmacHex(cfg.secret, `${PUBLIC_EVENT_REPORT_SIGNATURE_DOMAIN}.${timestampRaw}.${requestId}`);
  if (!timingSafeHexEqual(expectedDigest, signatureMatch[1])) return json({ ok: false, error: "Unauthorized" }, 401);
  try {
    const result = await cfg.db.prepare(PUBLIC_EVENT_REPORT_SQL).all();
    return json({ ok: true, rows: Array.isArray(result?.results) ? result.results : [] });
  } catch { return json({ ok: false, error: "Report unavailable" }, 503); }
}

function validTelegramBotToken(value) {
  return typeof value === "string" && /^\d{4,}:[A-Za-z0-9_-]{20,}$/.test(value.trim());
}

function parseTelegramWebhookUrl(value) {
  if (typeof value !== "string" || !value.trim()) return null;
  try {
    const url = new URL(value.trim());
    if (url.protocol !== "https:" || url.username || url.password || url.search || url.hash) return null;
    if (url.pathname !== "/api/telegram-faq") return null;
    return url.toString();
  } catch {
    return null;
  }
}

function telegramFaqReuseConfig(env) {
  if (env?.TELEGRAM_FAQ_REUSE_ENABLED !== "true") return { enabled: false };
  const secret = typeof env?.LEAD_WEBHOOK_SECRET === "string" ? env.LEAD_WEBHOOK_SECRET : "";
  const token = typeof env?.LEAD_NOTIFY_BOT_TOKEN === "string" ? env.LEAD_NOTIFY_BOT_TOKEN.trim() : "";
  const webhookUrl = parseTelegramWebhookUrl(env?.TELEGRAM_FAQ_WEBHOOK_URL);
  return {
    enabled: true,
    replyReady: utf8Bytes(secret) >= MIN_SECRET_BYTES && validTelegramBotToken(token),
    webhookReady: utf8Bytes(secret) >= MIN_SECRET_BYTES && validTelegramBotToken(token) && Boolean(webhookUrl),
    secret,
    token,
    webhookUrl,
  };
}

function validTelegramChatId(value) {
  return typeof value === "string" && /^-?\d{1,20}$/.test(value.trim());
}

function publicMonitorRelayConfig(env) {
  if (env?.PUBLIC_MONITOR_RELAY_ENABLED !== "true") return { enabled: false };
  const secret = typeof env?.PUBLIC_MONITOR_RELAY_SECRET === "string" ? env.PUBLIC_MONITOR_RELAY_SECRET : "";
  const token = typeof env?.LEAD_NOTIFY_BOT_TOKEN === "string" ? env.LEAD_NOTIFY_BOT_TOKEN.trim() : "";
  const chatId = typeof env?.LEAD_NOTIFY_CHAT_ID === "string" ? env.LEAD_NOTIFY_CHAT_ID.trim() : "";
  return {
    enabled: true,
    ready: utf8Bytes(secret) >= MIN_SECRET_BYTES && validTelegramBotToken(token) && validTelegramChatId(chatId),
    secret,
    token,
    chatId,
  };
}

function validatePayload(payload, headerRequestId, timestampSeconds) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  if (payload.schema !== "ai-skill-lab.lead.v2") return null;
  if (payload.requestId !== headerRequestId) return null;
  if (!UUID_V4.test(payload.requestId)) return null;
  if (!validText(payload.name, 80, { required: true })) return null;
  if (!ALLOWED_AUDIENCES.has(payload.audience)) return null;
  if (!validText(payload.contact, 120, { required: true })) return null;
  if (!validText(payload.goal ?? "", 600)) return null;
  if (!validText(payload.program ?? "", 80)) return null;
  if (!ALLOWED_LOCALES.has(payload.locale)) return null;
  if (payload.privacyConsent !== true) return null;
  if (typeof payload.adultConfirmed !== "boolean") return null;
  if (payload.source !== "ai-skill-lab") return null;
  if (typeof payload.ipToken !== "string" || !/^[0-9a-f]{64}$/.test(payload.ipToken)) return null;
  if (payload.sourcePath !== undefined) {
    if (!validText(payload.sourcePath, 180)) return null;
    if (!payload.sourcePath.startsWith("/") || payload.sourcePath.startsWith("//")) return null;
  }

  const youthProgram = typeof payload.program === "string" && (payload.program.startsWith("kids-") || payload.program.startsWith("teens-"));
  if ((youthProgram || payload.audience === "parent" || payload.audience === "teen") && payload.adultConfirmed !== true) return null;
  if (typeof payload.program === "string" && payload.program.startsWith("kids-") && payload.audience !== "parent") return null;

  if (typeof payload.receivedAt !== "string") return null;
  const receivedMs = Date.parse(payload.receivedAt);
  if (!Number.isFinite(receivedMs) || new Date(receivedMs).toISOString() !== payload.receivedAt) return null;
  if (Math.abs(receivedMs - timestampSeconds * 1000) > MAX_SKEW_SECONDS * 1000) return null;

  const expiresAt = new Date(receivedMs + RETENTION_DAYS * 86_400_000).toISOString();
  return {
    requestId: payload.requestId,
    receivedAt: payload.receivedAt,
    expiresAt,
    schema: payload.schema,
    name: payload.name,
    audience: payload.audience,
    contact: payload.contact,
    goal: payload.goal ?? "",
    program: payload.program ?? "",
    locale: payload.locale,
    privacyConsent: 1,
    adultConfirmed: payload.adultConfirmed ? 1 : 0,
    source: payload.source,
    sourcePath: payload.sourcePath ?? null,
    ipToken: payload.ipToken,
  };
}

function validateRouteRatePayload(payload, headerRequestId) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  if (payload.schema !== ROUTE_RATE_SCHEMA) return null;
  if (payload.requestId !== headerRequestId || !UUID_V4.test(payload.requestId)) return null;
  if (typeof payload.ipToken !== "string" || !/^[0-9a-f]{64}$/.test(payload.ipToken)) return null;
  if (payload.hourlyLimit !== ROUTE_HOURLY_LIMIT) return null;
  if (!Number.isSafeInteger(payload.dailyLimit) || payload.dailyLimit < 1 || payload.dailyLimit > 1_000_000) return null;
  return {
    requestId: payload.requestId,
    ipToken: payload.ipToken,
    dailyLimit: payload.dailyLimit,
  };
}

export async function handleRouteRateLimit(request, env = {}, nowMs = Date.now()) {
  const cfg = routeRateConfig(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.ready) return json({ ok: false, error: "Rate gate unavailable" }, 503);

  const url = new URL(request.url);
  if (url.pathname !== ROUTE_RATE_PATH) return json({ ok: false, error: "Not found" }, 404);
  if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "POST" });

  const contentType = request.headers.get("content-type") || "";
  if (!/^application\/json(?:\s*;|$)/i.test(contentType)) return json({ ok: false, error: "Unsupported media type" }, 415);

  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > ROUTE_RATE_BODY_BYTES) {
    return json({ ok: false, error: "Request too large" }, 413);
  }

  const timestampRaw = request.headers.get("x-ai-skill-lab-timestamp") || "";
  const requestId = request.headers.get("x-ai-skill-lab-request-id") || "";
  const signatureRaw = request.headers.get("x-ai-skill-lab-route-signature") || "";
  const signatureMatch = SIGNATURE_V1.exec(signatureRaw);
  if (!/^[0-9]{10}$/.test(timestampRaw) || !UUID_V4.test(requestId) || !signatureMatch) {
    return json({ ok: false, error: "Unauthorized" }, 401);
  }

  const timestampSeconds = Number(timestampRaw);
  const nowSeconds = Math.floor(nowMs / 1000);
  if (!Number.isSafeInteger(timestampSeconds) || Math.abs(nowSeconds - timestampSeconds) > MAX_SKEW_SECONDS) {
    return json({ ok: false, error: "Unauthorized" }, 401);
  }

  const rawBytes = new Uint8Array(await request.arrayBuffer());
  if (rawBytes.byteLength > ROUTE_RATE_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);
  let rawBody;
  try {
    rawBody = new TextDecoder("utf-8", { fatal: true }).decode(rawBytes);
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }

  const expectedDigest = await hmacHex(
    cfg.secret,
    `route-rate-v1.${timestampRaw}.${requestId}.${rawBody}`,
  );
  if (!timingSafeHexEqual(expectedDigest, signatureMatch[1])) {
    return json({ ok: false, error: "Unauthorized" }, 401);
  }

  let payload;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }
  const validated = validateRouteRatePayload(payload, requestId);
  if (!validated) return json({ ok: false, error: "Invalid rate request" }, 400);

  try {
    const coarse = await cfg.rateLimiter.limit({ key: `route:${validated.ipToken}` });
    if (!coarse?.success) {
      logReceiver("warn", "route_rate_limited", { requestId, status: 429 });
      return json({ ok: false, error: "Too many requests" }, 429, { "Retry-After": "60" });
    }
  } catch {
    logReceiver("error", "route_rate_binding_error", { requestId, status: 503 });
    return json({ ok: false, error: "Rate gate unavailable" }, 503);
  }

  let result;
  try {
    result = await cfg.db.prepare(ROUTE_RATE_INSERT_SQL).bind(
      validated.requestId,
      validated.ipToken,
      nowSeconds,
      validated.ipToken,
      nowSeconds - ROUTE_WINDOW_SECONDS,
      ROUTE_HOURLY_LIMIT,
      nowSeconds - ROUTE_DAY_SECONDS,
      validated.dailyLimit,
    ).run();
  } catch {
    logReceiver("error", "route_rate_db_error", { requestId, status: 503 });
    return json({ ok: false, error: "Rate gate unavailable" }, 503);
  }

  if (result?.meta?.changes !== 1) {
    logReceiver("warn", "route_rate_limited", { requestId, status: 429 });
    return json({ ok: false, error: "Too many requests" }, 429, { "Retry-After": String(ROUTE_WINDOW_SECONDS) });
  }

  logReceiver("info", "route_rate_allowed", { requestId, status: 200 });
  return json({ ok: true, requestId });
}

function validatePublicMonitorFailure(item) {
  if (!item || typeof item !== "object" || Array.isArray(item)) return null;
  const url = PUBLIC_MONITOR_TARGET_URLS[item.name];
  if (!url || item.expected !== 200) return null;

  if (item.actual === null) {
    if (typeof item.error !== "string" || !/^request_error=[A-Za-z][A-Za-z0-9_]{0,63}$/.test(item.error)) return null;
  } else {
    if (!Number.isSafeInteger(item.actual) || item.actual < 100 || item.actual > 599) return null;
    const statusErrors = new Set([`unexpected_status=${item.actual}`, `http_error=${item.actual}`]);
    if (!statusErrors.has(item.error)) return null;
  }
  return {
    name: item.name,
    url,
    expected: 200,
    actual: item.actual,
    error: item.error,
  };
}

function validPublicMonitorAlertPayload(payload, requestId) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  if (payload.schema !== PUBLIC_MONITOR_ALERT_SCHEMA) return null;
  if (payload.requestId !== requestId || !UUID_V4.test(payload.requestId)) return null;
  if (!Array.isArray(payload.failures) || payload.failures.length < 1 || payload.failures.length > 5) return null;

  const seen = new Set();
  const failures = [];
  for (const item of payload.failures) {
    const validated = validatePublicMonitorFailure(item);
    if (!validated || seen.has(validated.name)) return null;
    seen.add(validated.name);
    failures.push(validated);
  }
  return { requestId: payload.requestId, failures };
}

function formatPublicMonitorAlert(failures) {
  const lines = ["AI Skill Lab P27.7 public GET monitor failed."];
  for (const item of failures) {
    const observed = item.actual === null ? item.error : item.actual;
    lines.push(`- ${item.name}: expected=200 observed=${observed} url=${item.url}`);
  }
  return lines.join("\n");
}

export async function handlePublicMonitorAlert(request, env = {}, nowMs = Date.now(), fetchImpl = fetch) {
  const cfg = publicMonitorRelayConfig(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.ready) return json({ ok: false, error: "Monitor relay unavailable" }, 503);

  const url = new URL(request.url);
  if (url.pathname !== PUBLIC_MONITOR_ALERT_PATH) return json({ ok: false, error: "Not found" }, 404);
  if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "POST" });

  const contentType = request.headers.get("content-type") || "";
  if (!/^application\/json(?:\s*;|$)/i.test(contentType)) return json({ ok: false, error: "Unsupported media type" }, 415);

  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > PUBLIC_MONITOR_ALERT_BODY_BYTES) {
    return json({ ok: false, error: "Request too large" }, 413);
  }

  const timestampRaw = request.headers.get("x-ai-skill-lab-timestamp") || "";
  const requestId = request.headers.get("x-ai-skill-lab-request-id") || "";
  const signatureRaw = request.headers.get("x-ai-skill-lab-public-monitor-signature") || "";
  const signatureMatch = SIGNATURE_V1.exec(signatureRaw);
  if (!/^[0-9]{10}$/.test(timestampRaw) || !UUID_V4.test(requestId) || !signatureMatch) {
    return json({ ok: false, error: "Unauthorized" }, 401);
  }

  const timestampSeconds = Number(timestampRaw);
  if (!Number.isSafeInteger(timestampSeconds) || Math.abs(Math.floor(nowMs / 1000) - timestampSeconds) > MAX_SKEW_SECONDS) {
    return json({ ok: false, error: "Unauthorized" }, 401);
  }

  const rawBytes = new Uint8Array(await request.arrayBuffer());
  if (rawBytes.byteLength > PUBLIC_MONITOR_ALERT_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);

  let rawBody;
  try {
    rawBody = new TextDecoder("utf-8", { fatal: true }).decode(rawBytes);
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }

  const expectedDigest = await hmacHex(
    cfg.secret,
    `${PUBLIC_MONITOR_SIGNATURE_DOMAIN}.${timestampRaw}.${requestId}.${rawBody}`,
  );
  if (!timingSafeHexEqual(expectedDigest, signatureMatch[1])) return json({ ok: false, error: "Unauthorized" }, 401);

  let payload;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }
  const validated = validPublicMonitorAlertPayload(payload, requestId);
  if (!validated) return json({ ok: false, error: "Invalid monitor alert" }, 400);

  try {
    const response = await fetchImpl(`https://api.telegram.org/bot${cfg.token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: cfg.chatId,
        text: formatPublicMonitorAlert(validated.failures),
        disable_web_page_preview: true,
      }),
      signal: AbortSignal.timeout(NOTIFY_TIMEOUT_MS),
    });
    if (!response.ok) {
      logReceiver("warn", "public_monitor_alert_failed", { requestId, status: response.status });
      return json({ ok: false, error: "Monitor relay unavailable" }, 502);
    }
  } catch {
    logReceiver("warn", "public_monitor_alert_failed", { requestId, status: 0 });
    return json({ ok: false, error: "Monitor relay unavailable" }, 502);
  }

  logReceiver("info", "public_monitor_alert_sent", { requestId, status: 200 });
  return json({ ok: true, requestId });
}

function validTelegramFaqReplyPayload(payload, requestId) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  if (payload.schema !== TELEGRAM_FAQ_REPLY_SCHEMA) return null;
  if (payload.requestId !== requestId || !UUID_V4.test(payload.requestId)) return null;
  if (typeof payload.chatId !== "string" || !/^-?\d{1,20}$/.test(payload.chatId)) return null;
  if (!validText(payload.text, TELEGRAM_MESSAGE_MAX_CHARS, { required: true })) return null;
  if (payload.disableWebPagePreview !== true) return null;
  return {
    requestId: payload.requestId,
    chatId: payload.chatId,
    text: payload.text,
  };
}

export async function handleTelegramFaqReply(request, env = {}, nowMs = Date.now(), fetchImpl = fetch) {
  const cfg = telegramFaqReuseConfig(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.replyReady) return json({ ok: false, error: "Telegram relay unavailable" }, 503);

  const url = new URL(request.url);
  if (url.pathname !== TELEGRAM_FAQ_REPLY_PATH) return json({ ok: false, error: "Not found" }, 404);
  if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "POST" });

  const contentType = request.headers.get("content-type") || "";
  if (!/^application\/json(?:\s*;|$)/i.test(contentType)) return json({ ok: false, error: "Unsupported media type" }, 415);

  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > TELEGRAM_FAQ_REPLY_BODY_BYTES) {
    return json({ ok: false, error: "Request too large" }, 413);
  }

  const timestampRaw = request.headers.get("x-ai-skill-lab-timestamp") || "";
  const requestId = request.headers.get("x-ai-skill-lab-request-id") || "";
  const signatureRaw = request.headers.get("x-ai-skill-lab-telegram-relay-signature") || "";
  const signatureMatch = SIGNATURE_V1.exec(signatureRaw);
  if (!/^[0-9]{10}$/.test(timestampRaw) || !UUID_V4.test(requestId) || !signatureMatch) {
    return json({ ok: false, error: "Unauthorized" }, 401);
  }

  const timestampSeconds = Number(timestampRaw);
  if (!Number.isSafeInteger(timestampSeconds) || Math.abs(Math.floor(nowMs / 1000) - timestampSeconds) > MAX_SKEW_SECONDS) {
    return json({ ok: false, error: "Unauthorized" }, 401);
  }

  const rawBytes = new Uint8Array(await request.arrayBuffer());
  if (rawBytes.byteLength > TELEGRAM_FAQ_REPLY_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);

  let rawBody;
  try {
    rawBody = new TextDecoder("utf-8", { fatal: true }).decode(rawBytes);
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }

  const expectedDigest = await hmacHex(
    cfg.secret,
    `${TELEGRAM_REPLY_SIGNATURE_DOMAIN}.${timestampRaw}.${requestId}.${rawBody}`,
  );
  if (!timingSafeHexEqual(expectedDigest, signatureMatch[1])) return json({ ok: false, error: "Unauthorized" }, 401);

  let payload;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }
  const validated = validTelegramFaqReplyPayload(payload, requestId);
  if (!validated) return json({ ok: false, error: "Invalid relay request" }, 400);

  try {
    const response = await fetchImpl(`https://api.telegram.org/bot${cfg.token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: validated.chatId,
        text: validated.text,
        disable_web_page_preview: true,
      }),
      signal: AbortSignal.timeout(NOTIFY_TIMEOUT_MS),
    });
    if (!response.ok) {
      logReceiver("warn", "telegram_reply_failed", { requestId, status: response.status });
      return json({ ok: false, error: "Telegram relay unavailable" }, 502);
    }
  } catch {
    logReceiver("warn", "telegram_reply_failed", { requestId, status: 0 });
    return json({ ok: false, error: "Telegram relay unavailable" }, 502);
  }

  logReceiver("info", "telegram_reply_sent", { requestId, status: 200 });
  return json({ ok: true, requestId });
}

export async function ensureTelegramFaqWebhook(env = {}, fetchImpl = fetch) {
  const cfg = telegramFaqReuseConfig(env);
  if (!cfg.enabled) return { skipped: true };
  if (!cfg.webhookReady) {
    logReceiver("warn", "telegram_webhook_sync_failed", { status: 503 });
    return { ok: false };
  }

  try {
    const infoResponse = await fetchImpl(`https://api.telegram.org/bot${cfg.token}/getWebhookInfo`, {
      method: "GET",
      signal: AbortSignal.timeout(NOTIFY_TIMEOUT_MS),
    });
    if (!infoResponse.ok) {
      logReceiver("warn", "telegram_webhook_sync_failed", { status: infoResponse.status });
      return { ok: false };
    }
    const info = await infoResponse.json();
    if (info?.ok === true && info?.result?.url === cfg.webhookUrl) {
      logReceiver("info", "telegram_webhook_in_sync", { status: 200 });
      return { ok: true, changed: false };
    }

    const secretToken = await hmacHex(cfg.secret, TELEGRAM_WEBHOOK_SECRET_DOMAIN);
    const setResponse = await fetchImpl(`https://api.telegram.org/bot${cfg.token}/setWebhook`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: cfg.webhookUrl,
        secret_token: secretToken,
        allowed_updates: ["message"],
        drop_pending_updates: false,
      }),
      signal: AbortSignal.timeout(NOTIFY_TIMEOUT_MS),
    });
    if (!setResponse.ok) {
      logReceiver("warn", "telegram_webhook_sync_failed", { status: setResponse.status });
      return { ok: false };
    }
    const result = await setResponse.json();
    if (result?.ok !== true) {
      logReceiver("warn", "telegram_webhook_sync_failed", { status: 502 });
      return { ok: false };
    }
    logReceiver("info", "telegram_webhook_registered", { status: 200 });
    return { ok: true, changed: true };
  } catch {
    logReceiver("warn", "telegram_webhook_sync_failed", { status: 0 });
    return { ok: false };
  }
}

async function notifyNewLead(env, row) {
  const token = typeof env?.LEAD_NOTIFY_BOT_TOKEN === "string" ? env.LEAD_NOTIFY_BOT_TOKEN : "";
  const chatId = typeof env?.LEAD_NOTIFY_CHAT_ID === "string" ? env.LEAD_NOTIFY_CHAT_ID : "";
  if (!token || !chatId) return { skipped: true };

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), NOTIFY_TIMEOUT_MS);
  try {
    const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: [
          "AI Skill Lab: new application",
          `requestId: ${row.requestId}`,
          `receivedAt: ${row.receivedAt}`,
          `audience: ${row.audience}`,
          `locale: ${row.locale}`,
        ].join("\n"),
        disable_web_page_preview: true,
      }),
      signal: controller.signal,
    });
    if (!response.ok) throw new Error("notify response not ok");
    logReceiver("info", "notify_sent", { requestId: row.requestId, status: response.status });
    return { sent: true };
  } catch {
    logReceiver("warn", "notify_failed", { requestId: row.requestId, status: 0 });
    return { sent: false };
  } finally {
    clearTimeout(timer);
  }
}

export async function handleReceiver(request, env = {}, nowMs = Date.now(), ctx = null) {
  const cfg = config(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.ready) return json({ ok: false, error: "Receiver unavailable" }, 503);

  const url = new URL(request.url);
  if (url.pathname !== "/r101b/lead") return json({ ok: false, error: "Not found" }, 404);
  if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "POST" });

  const contentType = request.headers.get("content-type") || "";
  if (!/^application\/json(?:\s*;|$)/i.test(contentType)) return json({ ok: false, error: "Unsupported media type" }, 415);

  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > MAX_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);

  const timestampRaw = request.headers.get("x-ai-skill-lab-timestamp") || "";
  const requestId = request.headers.get("x-ai-skill-lab-request-id") || "";
  const signatureRaw = request.headers.get("x-ai-skill-lab-signature") || "";
  const signatureMatch = SIGNATURE_V1.exec(signatureRaw);
  if (!/^[0-9]{10}$/.test(timestampRaw) || !UUID_V4.test(requestId) || !signatureMatch) return json({ ok: false, error: "Unauthorized" }, 401);

  const timestampSeconds = Number(timestampRaw);
  if (!Number.isSafeInteger(timestampSeconds) || Math.abs(Math.floor(nowMs / 1000) - timestampSeconds) > MAX_SKEW_SECONDS) {
    return json({ ok: false, error: "Unauthorized" }, 401);
  }

  const rawBytes = new Uint8Array(await request.arrayBuffer());
  if (rawBytes.byteLength > MAX_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);

  let rawBody;
  try {
    rawBody = new TextDecoder("utf-8", { fatal: true }).decode(rawBytes);
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }

  const expectedDigest = await hmacHex(cfg.secret, `${timestampRaw}.${requestId}.${rawBody}`);
  if (!timingSafeHexEqual(expectedDigest, signatureMatch[1])) return json({ ok: false, error: "Unauthorized" }, 401);

  let payload;
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }

  const row = validatePayload(payload, requestId, timestampSeconds);
  if (!row) return json({ ok: false, error: "Invalid application" }, 400);

  let limitResult;
  try {
    limitResult = await cfg.rateLimiter.limit({ key: `lead:${row.ipToken}` });
  } catch {
    logReceiver("error", "rate_limit_error", { requestId, status: 503 });
    return json({ ok: false, error: "Receiver unavailable" }, 503);
  }
  if (!limitResult?.success) {
    logReceiver("warn", "rate_limited", { requestId, status: 429 });
    return json({ ok: false, error: "Too many requests" }, 429, { "Retry-After": "60" });
  }

  let result;
  try {
    result = await cfg.db.prepare(`
      INSERT INTO lead_intake_r101b (
        request_id, received_at, expires_at, schema, name, audience, contact, goal,
        program, locale, privacy_consent, adult_confirmed, source, source_path
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(request_id) DO NOTHING
    `).bind(
      row.requestId,
      row.receivedAt,
      row.expiresAt,
      row.schema,
      row.name,
      row.audience,
      row.contact,
      row.goal,
      row.program,
      row.locale,
      row.privacyConsent,
      row.adultConfirmed,
      row.source,
      row.sourcePath,
    ).run();
  } catch {
    logReceiver("error", "db_error", { requestId, status: 503 });
    return json({ ok: false, error: "Receiver unavailable" }, 503);
  }

  if (result?.meta?.changes !== 1) {
    logReceiver("warn", "duplicate", { requestId, status: 409 });
    return json({ ok: false, error: "Duplicate request" }, 409);
  }
  logReceiver("info", "inserted", { requestId, status: 200 });
  const notification = notifyNewLead(env, row);
  if (ctx && typeof ctx.waitUntil === "function") ctx.waitUntil(notification);
  else await notification;
  return json({ ok: true, requestId });
}

export async function cleanupExpired(env = {}, nowMs = Date.now()) {
  if (env?.LEAD_RECEIVER_ENABLED !== "true") return { skipped: true };
  if (!env?.DB || typeof env.DB.prepare !== "function") return { skipped: true };
  const cutoff = new Date(nowMs).toISOString();
  const result = await env.DB.prepare("DELETE FROM lead_intake_r101b WHERE expires_at <= ?").bind(cutoff).run();
  logReceiver("info", "retention_cleanup", { deleted: Number(result?.meta?.changes ?? 0) });
  return result;
}

export async function cleanupRouteRateEvents(env = {}, nowMs = Date.now()) {
  if (env?.ROUTE_RATE_LIMIT_ENABLED !== "true") return { skipped: true };
  if (!env?.DB || typeof env.DB.prepare !== "function") return { skipped: true };
  const cutoff = Math.floor(nowMs / 1000) - ROUTE_DAY_SECONDS;
  const result = await env.DB.prepare("DELETE FROM route_rate_event_r159 WHERE occurred_at < ?").bind(cutoff).run();
  logReceiver("info", "route_rate_cleanup", { deleted: Number(result?.meta?.changes ?? 0) });
  return result;
}

const workerHandler = {
  fetch(request, env, ctx) {
    const pathname = new URL(request.url).pathname;
    if (pathname === ROUTE_RATE_PATH) return handleRouteRateLimit(request, env, Date.now());
    if (pathname === PUBLIC_EVENT_PATH) return handlePublicEvent(request, env, Date.now());
    if (pathname === PUBLIC_EVENT_REPORT_PATH) return handlePublicEventReport(request, env, Date.now());
    if (pathname === TELEGRAM_FAQ_REPLY_PATH) return handleTelegramFaqReply(request, env, Date.now());
    if (pathname === PUBLIC_MONITOR_ALERT_PATH) return handlePublicMonitorAlert(request, env, Date.now());
    return handleReceiver(request, env, Date.now(), ctx);
  },
  scheduled(_controller, env, ctx) {
    ctx.waitUntil(Promise.all([
      cleanupExpired(env),
      cleanupRouteRateEvents(env),
      ensureTelegramFaqWebhook(env),
    ]));
  },
};

export default workerHandler;
