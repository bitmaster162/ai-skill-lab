import { createHmac } from "node:crypto";
import { NextResponse } from "next/server";

export const runtime = "nodejs";

const MAX_BODY_BYTES = 20_000;
const ALLOWED_AUDIENCES = new Set(["adult", "parent", "teen", "business"]);
const ALLOWED_LOCALES = new Set(["ru", "en"]);
const YOUTH_PROGRAM_PREFIXES = ["kids-", "teens-"];

function clean(value: unknown, max = 600) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
}

function accepted(value: unknown) {
  return clean(value, 12) === "yes";
}

function copy(locale: string) {
  const en = locale === "en";
  return {
    required: en ? "Please provide your name and contact" : "Заполните имя и контакт",
    consent: en ? "Please accept the privacy notice" : "Подтвердите согласие с правилами конфиденциальности",
    adult: en ? "A verified adult contact is required for youth programs" : "Для детской или подростковой программы нужен контакт и подтверждение взрослого",
    unconfigured: en ? "The form is not connected yet. Configure LEAD_WEBHOOK_URL." : "Форма пока не подключена. Настройте LEAD_WEBHOOK_URL.",
    unavailable: en ? "The application channel is temporarily unavailable" : "Канал заявок временно недоступен",
  };
}

export async function POST(request: Request) {
  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > MAX_BODY_BYTES) {
    return NextResponse.json({ ok: false, error: "Слишком большой запрос" }, { status: 413 });
  }

  let input: Record<string, unknown>;
  try {
    input = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ ok: false, error: "Некорректные данные" }, { status: 400 });
  }

  if (clean(input.website, 100)) {
    return NextResponse.json({ ok: true });
  }

  const rawAudience = clean(input.audience, 20);
  const rawLocale = clean(input.locale, 5);
  const locale = ALLOWED_LOCALES.has(rawLocale) ? rawLocale : "ru";
  const t = copy(locale);
  const program = clean(input.program, 80);
  const audience = ALLOWED_AUDIENCES.has(rawAudience) ? rawAudience : "adult";
  const youthProgram = YOUTH_PROGRAM_PREFIXES.some((prefix) => program.startsWith(prefix));

  if (!accepted(input.privacyConsent)) {
    return NextResponse.json({ ok: false, error: t.consent }, { status: 400 });
  }
  if ((youthProgram || audience === "parent" || audience === "teen") && !accepted(input.adultConfirmation)) {
    return NextResponse.json({ ok: false, error: t.adult }, { status: 400 });
  }
  if (program.startsWith("kids-") && audience !== "parent") {
    return NextResponse.json({ ok: false, error: t.adult }, { status: 400 });
  }

  const payload = {
    schema: "ai-skill-lab.lead.v2",
    name: clean(input.name, 80),
    audience,
    contact: clean(input.contact, 120),
    goal: clean(input.goal, 600),
    program,
    locale,
    privacyConsent: true,
    adultConfirmed: accepted(input.adultConfirmation),
    source: "ai-skill-lab",
    receivedAt: new Date().toISOString(),
  };

  if (!payload.name || !payload.contact) {
    return NextResponse.json({ ok: false, error: t.required }, { status: 400 });
  }

  const webhook = process.env.LEAD_WEBHOOK_URL;
  if (!webhook) {
    return NextResponse.json({ ok: false, error: t.unconfigured }, { status: 503 });
  }

  const body = JSON.stringify(payload);
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const secret = process.env.LEAD_WEBHOOK_SECRET;
  if (secret) headers["X-AI-Skill-Lab-Signature"] = `sha256=${createHmac("sha256", secret).update(body).digest("hex")}`;

  try {
    const response = await fetch(webhook, {
      method: "POST",
      headers,
      body,
      signal: AbortSignal.timeout(8_000),
    });
    if (!response.ok) throw new Error(`Webhook returned ${response.status}`);
  } catch {
    return NextResponse.json({ ok: false, error: t.unavailable }, { status: 502 });
  }

  return NextResponse.json({ ok: true });
}
