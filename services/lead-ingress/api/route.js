import fs from "node:fs";
import { randomUUID } from "node:crypto";

const FACTS = JSON.parse(fs.readFileSync(new URL("../commercial_facts.json", import.meta.url), "utf8"));
const MAX_BODY_BYTES = 12_000;
const MAX_INPUT_CHARS = 8_000;
const OPENROUTER_TIMEOUT_MS = 8_000;
const ALLOWED_AUDIENCES = new Set(["adult", "kids", "teens", "business"]);
const ALLOWED_LOCALES = new Set(["ru", "en"]);
const EVENT_SCHEMA = "ai-skill-lab.route-event.v1";
const LOG_FIELDS = new Set(["requestId", "status", "mode"]);
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

function logRoute(level, event, fields = {}) {
  const record = { schema: EVENT_SCHEMA, component: "route", event };
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

function configuredModels(value) {
  if (typeof value !== "string") return [];
  return value.split(",").map((x) => x.trim()).filter((x) => x && x.endsWith(":free")).slice(0, 6);
}

function config(env) {
  if (env.ROUTE_API_ENABLED !== "true") return { enabled: false };
  const origins = configuredOrigins(env.ROUTE_ALLOWED_ORIGINS);
  const rateLimitReady = env.ROUTE_RATE_LIMIT_READY === "true";
  const dailyLimitReady = env.ROUTE_DAILY_LIMIT_READY === "true";
  return {
    enabled: true,
    ready: Boolean(origins && rateLimitReady && dailyLimitReady),
    origins,
    key: typeof env.OPENROUTER_API_KEY === "string" ? env.OPENROUTER_API_KEY.trim() : "",
    models: configuredModels(env.OPENROUTER_MODELS),
  };
}

function countChars(value) {
  return [...String(value)].length;
}

function hasSecret(value) {
  return SECRET_PATTERNS.some((pattern) => pattern.test(value));
}

function exactText(value, max) {
  if (typeof value !== "string") throw new Error("invalid-field");
  const trimmed = value.trim();
  if (countChars(trimmed) > max) throw new Error("too-long");
  return trimmed;
}

function allMoneyTokens(value) {
  const raw = String(value).match(/(?:\$\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s?\$)/g) || [];
  return raw.map((token) => {
    const digits = token.replace(/\$/g, "").replace(/\s+/g, "");
    return `$${digits}`;
  });
}

function sanitizeGoalMoney(value) {
  return String(value).replace(/(?:\$\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s?\$)/g, (token) => {
    const normalized = allMoneyTokens(token)[0];
    return AUTHORIZED_MONEY.has(normalized) ? token : "[unsupported price removed]";
  });
}

function commercialPackages(audience, locale) {
  const en = locale === "en";
  if (audience !== "business") {
    return FACTS.tracks[audience].map((plan) => ({
      id: `${audience}:${plan.id}`,
      name: plan.name,
      price: plan.price,
      sessions: en ? plan.sessions_en : plan.sessions_ru,
    }));
  }
  const b = FACTS.business;
  return [
    {
      id: "business:workflow_audit",
      name: en ? b.workflow_audit.name_en : b.workflow_audit.name_ru,
      price: b.workflow_audit.price,
      sessions: en ? "fixed scope" : "фиксированный scope",
    },
    {
      id: "business:team_training",
      name: en ? b.team_training.name_en : b.team_training.name_ru,
      price: en ? `from ${b.team_training.price_from_per_session}/session` : `от ${b.team_training.price_from_per_session}/сессия`,
      sessions: en ? `minimum ${b.team_training.min_sessions} sessions` : `минимум ${b.team_training.min_sessions} занятия`,
    },
    {
      id: "business:implementation_pilot",
      name: en ? b.implementation_pilot.name_en : b.implementation_pilot.name_ru,
      price: en ? `from ${b.implementation_pilot.price_from}` : `от ${b.implementation_pilot.price_from}`,
      sessions: en ? `scope cap ${b.implementation_pilot.scope_cap_hours} hours` : `потолок scope ${b.implementation_pilot.scope_cap_hours} часов`,
    },
  ];
}

function authorizedMoney() {
  const tokens = new Set([FACTS.diagnostic.price]);
  for (const plans of Object.values(FACTS.tracks)) for (const plan of plans) tokens.add(plan.price);
  tokens.add(FACTS.family.price);
  const b = FACTS.business;
  tokens.add(b.workflow_audit.price);
  tokens.add(b.team_training.price_from_per_session);
  tokens.add(b.team_training.total_from);
  tokens.add(b.implementation_pilot.price_from);
  for (const item of Object.values(FACTS.recurring)) tokens.add(item.price_monthly);
  return tokens;
}

const AUTHORIZED_MONEY = authorizedMoney();

function introStep(locale) {
  return locale === "en" ? "Free 15-minute intro call" : "Бесплатный звонок-знакомство · 15 минут";
}

function diagnosticStep(locale) {
  const d = FACTS.diagnostic;
  return locale === "en"
    ? `Diagnostic session ${d.price} · ${FACTS.session_duration_minutes} minutes · ${d.credit_en}`
    : `Диагностика ${d.price} · ${FACTS.session_duration_minutes} минут · ${d.credit_ru}`;
}

function fallbackPackage(input, table) {
  if (input.audience === "business") {
    if (input.answers.includes("automate") || /automat|agent|workflow/i.test(input.goal)) return table.find((x) => x.id === "business:implementation_pilot");
    if (input.answers.includes("team")) return table.find((x) => x.id === "business:team_training");
    return table.find((x) => x.id === "business:workflow_audit");
  }
  const depth = input.answers.includes("deep") ? 2 : input.answers.includes("core") ? 1 : 0;
  return table[Math.min(depth, table.length - 1)];
}

function fallbackResult(input, table) {
  const pkg = fallbackPackage(input, table);
  const third = input.locale === "en"
    ? `Start ${pkg.name} with one bounded project and a review checkpoint.`
    : `Начать ${pkg.name} с одного ограниченного проекта и контрольной точки проверки.`;
  const rawGoal = input.goal || (input.locale === "en" ? "route selection" : "подбор маршрута");
  const goal = sanitizeGoalMoney(rawGoal);
  const brief = input.locale === "en"
    ? `Route request: ${pkg.name}. Goal: ${goal}`.slice(0, 600)
    : `Запрос на маршрут: ${pkg.name}. Цель: ${goal}`.slice(0, 600);
  return { status: "fallback", package: pkg, steps: [introStep(input.locale), diagnosticStep(input.locale), third], brief };
}

function validateInput(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("invalid-body");
  const audience = exactText(input.audience, 20);
  const locale = exactText(input.locale, 5);
  if (!ALLOWED_AUDIENCES.has(audience) || !ALLOWED_LOCALES.has(locale)) throw new Error("invalid-enum");
  if (!Array.isArray(input.answers) || input.answers.length !== 3) throw new Error("answers");
  const answers = input.answers.map((x) => exactText(x, 120));
  if (answers[0] !== audience) throw new Error("audience-answer-mismatch");
  const goal = exactText(input.goal ?? "", 2_000);
  const joined = [audience, locale, ...answers, goal].join("\n");
  if (countChars(joined) > MAX_INPUT_CHARS) throw new Error("input-too-large");
  return { audience, locale, answers, goal, adultConfirmed: input.adultConfirmed === true };
}

function validateModelResult(value, input, table) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const pkg = value.package;
  if (!pkg || typeof pkg !== "object" || Array.isArray(pkg)) return null;
  const allowed = table.find((x) => x.id === pkg.id && x.name === pkg.name && x.price === pkg.price);
  if (!allowed) return null;
  if (!Array.isArray(value.steps) || value.steps.length !== 3 || value.steps.some((x) => typeof x !== "string" || countChars(x.trim()) > 240)) return null;
  const steps = value.steps.map((x) => x.trim());
  if (steps[0] !== introStep(input.locale) || steps[1] !== diagnosticStep(input.locale)) return null;
  if (typeof value.brief !== "string" || !value.brief.trim() || countChars(value.brief.trim()) > 600) return null;
  const combined = [...steps, value.brief, pkg.price].join("\n");
  if (hasSecret(combined)) return null;
  for (const token of allMoneyTokens(combined)) if (!AUTHORIZED_MONEY.has(token)) return null;
  return { status: "ok", package: allowed, steps, brief: value.brief.trim() };
}

function promptFor(input, table) {
  return [
    "You are AI Skill Lab's route finder.",
    "Use only the provided package table. Return JSON only with keys status, package, steps, brief.",
    "package must exactly copy id, name and price from the table.",
    `steps must contain exactly 3 strings. Step 1 must be exactly: ${JSON.stringify(introStep(input.locale))}.`,
    `Step 2 must be exactly: ${JSON.stringify(diagnosticStep(input.locale))}.`,
    "Step 3 must be concrete and bounded. Never promise results.",
    "Never mention any price not present in the provided authority table. Give no medical or psychological advice.",
    input.audience === "kids" ? "Address the parent or guardian, not the child." : "",
    "brief must be at most 600 characters and suitable for the free intro call.",
    `PACKAGE_TABLE=${JSON.stringify(table)}`,
    `PROFILE=${JSON.stringify(input)}`,
  ].filter(Boolean).join("\n");
}

async function callOpenRouter(cfg, input, table, fetchImpl) {
  if (!cfg.key || cfg.models.length === 0) return null;
  const system = promptFor(input, table);
  for (const model of cfg.models) {
    for (let attempt = 0; attempt < 2; attempt += 1) {
      let response;
      try {
        response = await fetchImpl("https://openrouter.ai/api/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${cfg.key}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model,
            messages: [{ role: "system", content: system }, { role: "user", content: input.goal || "Recommend a route." }],
            response_format: { type: "json_object" },
            temperature: 0.2,
          }),
          signal: AbortSignal.timeout(OPENROUTER_TIMEOUT_MS),
        });
      } catch {
        response = null;
      }
      if (!response?.ok) break;
      let payload;
      try { payload = await response.json(); } catch { payload = null; }
      const content = payload?.choices?.[0]?.message?.content;
      if (typeof content !== "string") continue;
      let parsed;
      try { parsed = JSON.parse(content); } catch { parsed = null; }
      const validated = validateModelResult(parsed, input, table);
      if (validated) return { result: validated, model };
    }
  }
  return null;
}

export async function handleRoute(request, env = process.env, fetchImpl = fetch) {
  if (request.method !== "POST") return json({ status: "error", error: "Method not allowed" }, 405, { Allow: "POST" });
  const cfg = config(env);
  if (!cfg.enabled) return json({ status: "error", error: "Not found" }, 404);
  if (!cfg.ready) return json({ status: "error", error: "Route service unavailable" }, 503);
  const origin = request.headers.get("origin");
  if (!origin || !cfg.origins.has(origin)) return json({ status: "error", error: "Request rejected" }, 403);
  const contentType = request.headers.get("content-type") || "";
  if (!/^application\/json(?:\s*;|$)/i.test(contentType)) return json({ status: "error", error: "Unsupported media type" }, 415);
  const declaredLength = Number(request.headers.get("content-length") || 0);
  if (Number.isFinite(declaredLength) && declaredLength > MAX_BODY_BYTES) return json({ status: "error", error: "Request too large" }, 413);
  const raw = Buffer.from(await request.arrayBuffer());
  if (raw.byteLength > MAX_BODY_BYTES) return json({ status: "error", error: "Request too large" }, 413);
  let input;
  try { input = validateInput(JSON.parse(raw.toString("utf8"))); } catch { return json({ status: "error", error: "Invalid route request" }, 400); }
  const joined = [input.audience, ...input.answers, input.goal].join("\n");
  if (hasSecret(joined)) return json({ status: "secret_detected", package: null, steps: [], brief: "" }, 400);
  const requestId = randomUUID();
  const table = commercialPackages(input.audience, input.locale);
  const ai = await callOpenRouter(cfg, input, table, fetchImpl);
  const result = ai?.result || fallbackResult(input, table);
  logRoute("info", "route_complete", { requestId, status: 200, mode: ai ? "ai" : "fallback" });
  return json({ ...result, requestId });
}

const routeHandler = {
  fetch(request) {
    return handleRoute(request);
  },
};

export default routeHandler;
