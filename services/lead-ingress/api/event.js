import { createHmac, randomUUID } from "node:crypto";
import { isIP } from "node:net";

const MAX_BODY_BYTES = 2_000;
const MIN_SECRET_BYTES = 32;
const WEBHOOK_TIMEOUT_MS = 5_000;
const ALLOWED_EVENTS = new Set([
  "lead_submit_ok",
  "lead_submit_error",
  "cal_click",
  "telegram_click",
  "whatsapp_click",
  "line_click",
  "email_click",
]);
const ALLOWED_LOCALES = new Set(["ru", "en"]);

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
  if (!value) return null;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.username || url.password) return null;
    return url;
  } catch {
    return null;
  }
}

function configuredOrigins(value) {
  if (!value) return null;
  const origins = new Set();
  for (const raw of value.split(",")) {
    const url = parseHttpsUrl(raw.trim());
    if (!url || url.pathname !== "/" || url.search || url.hash) return null;
    origins.add(url.origin);
  }
  return origins.size ? origins : null;
}

function config(env) {
  if (env.LEAD_INGRESS_ENABLED !== "true") return { enabled: false };
  const webhook = parseHttpsUrl(env.LEAD_WEBHOOK_URL);
  const origins = configuredOrigins(env.LEAD_ALLOWED_ORIGINS);
  const secret = env.LEAD_WEBHOOK_SECRET || "";
  const ready = Boolean(
    webhook &&
      origins &&
      Buffer.byteLength(secret, "utf8") >= MIN_SECRET_BYTES &&
      env.LEAD_RATE_LIMIT_READY === "true",
  );
  return { enabled: true, ready, webhook, origins, secret };
}

function signature(secret, timestamp, requestId, body) {
  return createHmac("sha256", secret)
    .update(`public-event-v1.${timestamp}.${requestId}.${body}`)
    .digest("hex");
}

function clientIp(request) {
  const raw = request.headers.get("x-forwarded-for") || "";
  const first = raw.split(",", 1)[0].trim();
  return isIP(first) ? first : null;
}

function ipToken(secret, ip) {
  return createHmac("sha256", secret)
    .update(`public-event-ip-v1:${ip}`)
    .digest("hex");
}

function validateInput(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) return null;
  const keys = Object.keys(input).sort();
  if (keys.join(",") !== "event,locale,page") return null;
  if (!ALLOWED_EVENTS.has(input.event)) return null;
  if (!ALLOWED_LOCALES.has(input.locale)) return null;
  if (typeof input.page !== "string" || !input.page.startsWith("/") || input.page.startsWith("//")) return null;
  if (Buffer.byteLength(input.page, "utf8") > 180 || input.page.includes("?") || input.page.includes("#")) return null;
  return { event: input.event, page: input.page, locale: input.locale };
}

export async function handlePublicEvent(request, env = process.env) {
  if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "POST" });
  const cfg = config(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.ready) return json({ ok: false, error: "Event counter unavailable" }, 503);

  const origin = request.headers.get("origin");
  if (!origin || !cfg.origins.has(origin)) return json({ ok: false, error: "Request rejected" }, 403);
  if (!/^application\/json(?:\s*;|$)/i.test(request.headers.get("content-type") || "")) {
    return json({ ok: false, error: "Unsupported media type" }, 415);
  }
  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > MAX_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);
  const raw = Buffer.from(await request.arrayBuffer());
  if (raw.byteLength > MAX_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);

  let input;
  try {
    input = JSON.parse(raw.toString("utf8"));
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }
  const validated = validateInput(input);
  if (!validated) return json({ ok: false, error: "Invalid event" }, 400);

  const ip = clientIp(request);
  if (!ip) return json({ ok: false, error: "Event counter unavailable" }, 503);

  const requestId = randomUUID();
  const occurredAt = new Date().toISOString();
  const body = JSON.stringify({
    schema: "ai-skill-lab.public-event.v1",
    requestId,
    occurredAt,
    event: validated.event,
    page: validated.page,
    locale: validated.locale,
    ipToken: ipToken(cfg.secret, ip),
  });
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const digest = signature(cfg.secret, timestamp, requestId, body);
  const endpoint = new URL("/e3/event", cfg.webhook);

  try {
    const downstream = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-AI-Skill-Lab-Timestamp": timestamp,
        "X-AI-Skill-Lab-Request-Id": requestId,
        "X-AI-Skill-Lab-Public-Event-Signature": `v1=${digest}`,
      },
      body,
      signal: AbortSignal.timeout(WEBHOOK_TIMEOUT_MS),
    });
    if (!downstream.ok) return json({ ok: false, error: "Event counter unavailable" }, 502);
  } catch {
    return json({ ok: false, error: "Event counter unavailable" }, 502);
  }
  return json({ ok: true });
}

export default {
  fetch(request) {
    return handlePublicEvent(request);
  },
};
