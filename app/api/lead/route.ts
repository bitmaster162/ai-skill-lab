import { NextResponse } from "next/server";

const MAX_BODY_BYTES = 20_000;
const ALLOWED_AUDIENCES = new Set(["adult", "parent", "teen", "business"]);
const ALLOWED_LOCALES = new Set(["ru", "en"]);

function clean(value: unknown, max = 600) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
}

function copy(locale: string) {
  const en = locale === "en";
  return {
    required: en ? "Please provide your name and contact" : "Заполните имя и контакт",
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
  const payload = {
    name: clean(input.name, 80),
    audience: ALLOWED_AUDIENCES.has(rawAudience) ? rawAudience : "adult",
    contact: clean(input.contact, 120),
    goal: clean(input.goal, 600),
    program: clean(input.program, 80),
    locale,
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

  try {
    const response = await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(8_000),
    });
    if (!response.ok) throw new Error(`Webhook returned ${response.status}`);
  } catch {
    return NextResponse.json({ ok: false, error: t.unavailable }, { status: 502 });
  }

  return NextResponse.json({ ok: true });
}
