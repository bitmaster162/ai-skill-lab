#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
errors=[];checks=0

def req(cond,msg):
    global checks
    checks+=1
    if not cond: errors.append(msg)

route=(ROOT/"services/lead-ingress/api/route.js").read_text(encoding="utf-8")
worker=(ROOT/"services/lead-receiver-cloudflare/src/index.js").read_text(encoding="utf-8")
schema=(ROOT/"schema/route_rate_event_r159.sql").read_text(encoding="utf-8").lower()
ru_source=(ROOT/"app/(ru)/privacy/page.tsx").read_text(encoding="utf-8")
en_source=(ROOT/"app/(en)/en/privacy/page.tsx").read_text(encoding="utf-8")
ru_static=(ROOT/"deploy/live/privacy.html").read_text(encoding="utf-8")
en_static=(ROOT/"deploy/live/en/privacy.html").read_text(encoding="utf-8")

for marker in [
    'request.headers.get("x-forwarded-for")',
    'route-ip-v1:',
    'checkRouteRate(request, cfg, fetchImpl)',
    'https://openrouter.ai/api/v1/chat/completions',
]:
    req(marker in route,f"route implementation missing {marker}")

handle_start=route.index("export async function handleRoute")
handle=route[handle_start:]
req(handle.index("if (hasSecret(joined))") < handle.index("checkRouteRate(request, cfg, fetchImpl)"),"secret rejection must precede exact rate gate")
req(handle.index("checkRouteRate(request, cfg, fetchImpl)") < handle.index("callOpenRouter(cfg, input, table, fetchImpl)"),"rate gate must precede model call")
req('DELETE FROM route_rate_event_r159 WHERE occurred_at < ?' in worker,"24h cleanup query missing")
req('ROUTE_DAY_SECONDS = 86_400' in worker,"24h cleanup constant missing")
req("raw_ip" not in schema and "ip_address" not in schema,"route-rate schema must not store raw IP")
for forbidden in ["goal","answers","audience","contact","name"]:
    req(forbidden not in schema,f"route-rate schema stores forbidden field {forbidden}")
for required in ["request_id","ip_token","occurred_at"]:
    req(required in schema,f"route-rate schema missing {required}")

ru_markers=[
    "AI-route и OpenRouter",
    "только после нажатия кнопки пользователем",
    "три ответа matcher и текст цели",
    "обнаруженный секрет блокируется до вызова модели",
    "через OpenRouter API",
    "сразу преобразует его в HMAC-token",
    "Сырой IP не записывается",
    "request ID, HMAC-token и техническая отметка времени",
    "cleanup удаляет rate-limit записи старше 24 часов",
    "не для рекламного профилирования",
]
en_markers=[
    "AI routing and OpenRouter",
    "only after the user presses the route button",
    "three matcher answers and the goal text",
    "detected secrets are blocked before the model is called",
    "through the OpenRouter API",
    "immediately converts it to an HMAC token",
    "raw IP is not written",
    "request ID, HMAC token and technical timestamp",
    "cleanup deletes rate-limit rows once they are older than 24 hours",
    "not for advertising profiling",
]
for text,label,markers in [
    (ru_source,"ru source",ru_markers),
    (en_source,"en source",en_markers),
    (ru_static,"ru static",ru_markers),
    (en_static,"en static",en_markers),
]:
    for marker in markers:
        req(marker in text,f"{label}: missing privacy marker {marker}")

req("/api/route" in ru_source and "/api/route" in en_source,"source privacy must name same-origin route endpoint")
req("/api/route" in ru_static and "/api/route" in en_static,"static privacy must name same-origin route endpoint")
req("ROUTE_PRIVACY_READY=false" in (ROOT/"services/lead-ingress/.env.example").read_text(encoding="utf-8"),"privacy gate must remain fail-closed in env example")

print(f"route_privacy_checks={checks} source=2 static=2 raw_ip_persisted=false cleanup_seconds=86400")
if errors:
    print("ROUTE_PRIVACY_DISCLOSURE_FAIL")
    for error in errors: print("FAIL:",error)
    raise SystemExit(1)
print("ROUTE_PRIVACY_DISCLOSURE_PASS")
