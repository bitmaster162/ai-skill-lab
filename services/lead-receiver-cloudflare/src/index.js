const MAX_BODY_BYTES = 20_000;
const MIN_SECRET_BYTES = 32;
const MAX_SKEW_SECONDS = 300;
const RETENTION_DAYS = 30;
const RATE_LIMIT_KEY = "lead-intake";
const ALLOWED_AUDIENCES = new Set(["adult", "parent", "teen", "business"]);
const ALLOWED_LOCALES = new Set(["ru", "en"]);
const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SIGNATURE_V1 = /^v1=([0-9a-f]{64})$/;

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
  };
}

export async function handleReceiver(request, env = {}, nowMs = Date.now()) {
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
    limitResult = await cfg.rateLimiter.limit({ key: RATE_LIMIT_KEY });
  } catch {
    return json({ ok: false, error: "Receiver unavailable" }, 503);
  }
  if (!limitResult?.success) {
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
    return json({ ok: false, error: "Receiver unavailable" }, 503);
  }

  if (result?.meta?.changes !== 1) return json({ ok: false, error: "Duplicate request" }, 409);
  return json({ ok: true, requestId });
}

export async function cleanupExpired(env = {}, nowMs = Date.now()) {
  if (env?.LEAD_RECEIVER_ENABLED !== "true") return { skipped: true };
  if (!env?.DB || typeof env.DB.prepare !== "function") return { skipped: true };
  const cutoff = new Date(nowMs).toISOString();
  return env.DB.prepare("DELETE FROM lead_intake_r101b WHERE expires_at <= ?").bind(cutoff).run();
}

export default {
  fetch(request, env) {
    return handleReceiver(request, env);
  },
  scheduled(_controller, env, ctx) {
    ctx.waitUntil(cleanupExpired(env));
  },
};
