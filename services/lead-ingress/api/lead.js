import { createHmac, randomUUID } from "node:crypto";

const MAX_BODY_BYTES = 20_000;
const WEBHOOK_TIMEOUT_MS = 8_000;
const MIN_SECRET_BYTES = 32;
const ALLOWED_AUDIENCES = new Set(["adult", "parent", "teen", "business"]);
const ALLOWED_LOCALES = new Set(["ru", "en"]);
const YOUTH_PROGRAM_PREFIXES = ["kids-", "teens-"];

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

function text(value, max) {
  if (value === undefined || value === null) return "";
  if (typeof value !== "string") throw new Error("invalid-field-type");
  const cleaned = value.trim();
  if (Buffer.byteLength(cleaned, "utf8") > max) throw new Error("field-too-large");
  return cleaned;
}

function yes(value) {
  return value === "yes";
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

function validPrivacyContact(value) {
  return typeof value === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

function config(env) {
  if (env.LEAD_INGRESS_ENABLED !== "true") return { enabled: false };

  const webhook = parseHttpsUrl(env.LEAD_WEBHOOK_URL);
  const origins = configuredOrigins(env.LEAD_ALLOWED_ORIGINS);
  const secret = env.LEAD_WEBHOOK_SECRET || "";
  const operator = (env.LEAD_LEGAL_OPERATOR_NAME || "").trim();
  const jurisdiction = (env.LEAD_LEGAL_JURISDICTION || "").trim();
  const privacyContact = (env.LEAD_PRIVACY_CONTACT || "").trim();
  const retentionDays = env.LEAD_RETENTION_DAYS;
  const rateLimitReady = env.LEAD_RATE_LIMIT_READY === "true";

  const ready = Boolean(
    webhook &&
      origins &&
      Buffer.byteLength(secret, "utf8") >= MIN_SECRET_BYTES &&
      operator &&
      jurisdiction &&
      validPrivacyContact(privacyContact) &&
      retentionDays === "30" &&
      rateLimitReady,
  );

  return {
    enabled: true,
    ready,
    webhook,
    origins,
    secret,
  };
}

function signature(secret, timestamp, requestId, body) {
  return createHmac("sha256", secret)
    .update(`${timestamp}.${requestId}.${body}`)
    .digest("hex");
}

function validateInput(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("invalid-body");

  const website = text(input.website, 100);
  if (website) return { honeypot: true };

  const name = text(input.name, 80);
  const contact = text(input.contact, 120);
  const goal = text(input.goal, 600);
  const program = text(input.program, 80);
  const sourcePath = text(input.sourcePath, 180);
  const audience = text(input.audience, 20);
  const locale = text(input.locale, 5);

  if (!name || !contact) throw new Error("required");
  if (!ALLOWED_AUDIENCES.has(audience)) throw new Error("audience");
  if (!ALLOWED_LOCALES.has(locale)) throw new Error("locale");
  if (!yes(input.privacyConsent)) throw new Error("consent");
  if (sourcePath && (!sourcePath.startsWith("/") || sourcePath.startsWith("//"))) throw new Error("source-path");

  const youthProgram = YOUTH_PROGRAM_PREFIXES.some((prefix) => program.startsWith(prefix));
  if ((youthProgram || audience === "parent" || audience === "teen") && !yes(input.adultConfirmation)) {
    throw new Error("adult-confirmation");
  }
  if (program.startsWith("kids-") && audience !== "parent") throw new Error("kids-parent");

  return {
    honeypot: false,
    payload: {
      schema: "ai-skill-lab.lead.v2",
      name,
      audience,
      contact,
      goal,
      program,
      locale,
      privacyConsent: true,
      adultConfirmed: yes(input.adultConfirmation),
      source: "ai-skill-lab",
      sourcePath: sourcePath || undefined,
    },
  };
}

export async function handleLead(request, env = process.env) {
  if (request.method !== "POST") {
    return json({ ok: false, error: "Method not allowed" }, 405, { Allow: "POST" });
  }

  const cfg = config(env);
  if (!cfg.enabled) return json({ ok: false, error: "Not found" }, 404);
  if (!cfg.ready) return json({ ok: false, error: "Application channel unavailable" }, 503);

  const origin = request.headers.get("origin");
  if (!origin || !cfg.origins.has(origin)) {
    return json({ ok: false, error: "Request rejected" }, 403);
  }

  const contentType = request.headers.get("content-type") || "";
  if (!/^application\/json(?:\s*;|$)/i.test(contentType)) {
    return json({ ok: false, error: "Unsupported media type" }, 415);
  }

  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > MAX_BODY_BYTES) {
    return json({ ok: false, error: "Request too large" }, 413);
  }

  const raw = Buffer.from(await request.arrayBuffer());
  if (raw.byteLength > MAX_BODY_BYTES) return json({ ok: false, error: "Request too large" }, 413);

  let input;
  try {
    input = JSON.parse(raw.toString("utf8"));
  } catch {
    return json({ ok: false, error: "Invalid data" }, 400);
  }

  let validated;
  try {
    validated = validateInput(input);
  } catch {
    return json({ ok: false, error: "Invalid application" }, 400);
  }

  if (validated.honeypot) return json({ ok: true });

  const requestId = randomUUID();
  const receivedAt = new Date().toISOString();
  const payload = { ...validated.payload, requestId, receivedAt };
  const body = JSON.stringify(payload);
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const digest = signature(cfg.secret, timestamp, requestId, body);

  let downstream;
  try {
    downstream = await fetch(cfg.webhook, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-AI-Skill-Lab-Timestamp": timestamp,
        "X-AI-Skill-Lab-Request-Id": requestId,
        "X-AI-Skill-Lab-Signature": `v1=${digest}`,
      },
      body,
      signal: AbortSignal.timeout(WEBHOOK_TIMEOUT_MS),
    });
  } catch {
    return json({ ok: false, error: "Application channel unavailable" }, 502);
  }

  if (!downstream.ok) return json({ ok: false, error: "Application channel unavailable" }, 502);
  return json({ ok: true, requestId });
}

export default {
  fetch(request) {
    return handleLead(request);
  },
};
