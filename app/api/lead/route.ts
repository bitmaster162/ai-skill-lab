import { NextResponse } from "next/server";

const MAX_BODY_BYTES = 20_000;

function clean(value: unknown, max = 600) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
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

  const payload = {
    name: clean(input.name, 80),
    audience: clean(input.audience, 20),
    contact: clean(input.contact, 120),
    goal: clean(input.goal, 600),
    source: "ai-academy-site",
    receivedAt: new Date().toISOString(),
  };

  if (!payload.name || !payload.contact) {
    return NextResponse.json({ ok: false, error: "Заполните имя и контакт" }, { status: 400 });
  }

  const webhook = process.env.LEAD_WEBHOOK_URL;
  if (!webhook) {
    return NextResponse.json(
      { ok: false, error: "Форма пока не подключена. Настройте LEAD_WEBHOOK_URL." },
      { status: 503 },
    );
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
    return NextResponse.json({ ok: false, error: "Канал заявок временно недоступен" }, { status: 502 });
  }

  return NextResponse.json({ ok: true });
}
