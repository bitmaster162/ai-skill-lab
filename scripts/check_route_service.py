#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
errors=[];checks=0

def req(cond,msg):
    global checks
    checks+=1
    if not cond: errors.append(msg)

authority=ROOT/"data/commercial_facts.json"
projection=ROOT/"services/lead-ingress/commercial_facts.json"
route=ROOT/"services/lead-ingress/api/route.js"
env_file=ROOT/"services/lead-ingress/.env.example"
service_vercel=ROOT/"services/lead-ingress/vercel.json"
site_vercel=ROOT/"deploy/live/vercel.json"
matcher=ROOT/"components/ProgramMatcher.tsx"
matcher_js=ROOT/"deploy/live/matcher-v2.js"
matcher_pages=[ROOT/"deploy/live/matcher.html",ROOT/"deploy/live/en/matcher.html"]

req(authority.is_file(),"commercial authority missing")
req(projection.is_file(),"route commercial projection missing")
if authority.is_file() and projection.is_file():
    req(authority.read_bytes()==projection.read_bytes(),"route commercial projection drift")

route_text=route.read_text(encoding="utf-8")
env_text=env_file.read_text(encoding="utf-8")
service_cfg=json.loads(service_vercel.read_text(encoding="utf-8"))
site_cfg=json.loads(site_vercel.read_text(encoding="utf-8"))
matcher_text=matcher.read_text(encoding="utf-8")
matcher_js_text=matcher_js.read_text(encoding="utf-8")
authority_json=json.loads(authority.read_text(encoding="utf-8"))
facts_line=next((line for line in matcher_js_text.splitlines() if line.startswith("const FACTS=")), "")
static_facts=None
if facts_line.endswith(";"):
    try: static_facts=json.loads(facts_line[len("const FACTS="):-1])
    except json.JSONDecodeError: static_facts=None
req(static_facts==authority_json,"static matcher commercial projection drift")

req('ROUTE_API_ENABLED !== "true"' in route_text,"route service must default fail-closed")
req('ROUTE_RATE_LIMIT_READY === "true"' in route_text,"hourly rate-limit readiness gate missing")
req('ROUTE_DAILY_LIMIT_READY === "true"' in route_text,"daily rate-limit readiness gate missing")
req('endsWith(":free")' in route_text,"OpenRouter model list must accept :free models only")
req("OPENROUTER_API_KEY" in route_text,"server-only OpenRouter key marker missing")
req("https://openrouter.ai/api/v1/chat/completions" in route_text,"OpenRouter endpoint missing")
req("MAX_INPUT_CHARS = 8_000" in route_text,"8000-character input cap missing")
req("secret_detected" in route_text,"secret rejection status missing")
for marker in ["sk-","ghp_","github_pat_","xox","AKIA","-----BEGIN","eyJ","{32,}"]:
    req(marker in route_text,f"secret detector marker missing: {marker}")
req('Бесплатный звонок-знакомство · 15 минут' in route_text,"RU intro-first step missing")
req('Free 15-minute intro call' in route_text,"EN intro-first step missing")
req('diagnosticStep(input.locale)' in route_text,"diagnostic second-step binding missing")
req("The first step is always the $120 diagnostic" not in route_text,"stale diagnostic-first prompt returned")
req("AUTHORIZED_MONEY" in route_text and "validateModelResult" in route_text,"price authority validation missing")
req("fallbackResult" in route_text,"deterministic fallback missing")
req("route_complete" in route_text,"metadata-only route event missing")

for line in route_text.splitlines():
    if "logRoute(" in line and '"route_complete"' in line:
        req("goal" not in line and "answers" not in line and "key" not in line,"route log may expose user input or key")

req("ROUTE_API_ENABLED=false" in env_text,"route API example must default disabled")
req("ROUTE_RATE_LIMIT_READY=false" in env_text,"hourly rate-limit example must default false")
req("ROUTE_DAILY_LIMIT_READY=false" in env_text,"daily rate-limit example must default false")
req("OPENROUTER_API_KEY=" in env_text and "OPENROUTER_MODELS=" in env_text,"OpenRouter env example missing")
req("50" not in "\n".join(line for line in env_text.splitlines() if "ROUTE_" in line),"unconfirmed daily numeric limit must not be hard-coded")

functions=service_cfg.get("functions",{})
req("api/route.js" in functions,"route function missing from ingress Vercel config")
req(functions.get("api/route.js",{}).get("maxDuration")==10,"route function maxDuration drift")

rewrites=site_cfg.get("rewrites",[])
req({"source":"/api/route","destination":"https://ai-skill-lab-ingress.vercel.app/api/route"} in rewrites,"same-origin /api/route rewrite missing")

for marker in ['fetch("/api/route"','fetch("/api/lead"','privacyConsent:"yes"','adultConfirmation:youth?"yes":""']:
    req(marker in matcher_text,f"matcher source contract missing {marker}")
req("localStorage" not in matcher_text and "sessionStorage" not in matcher_text,"matcher must not store input in browser storage")
req("not a promised outcome" in matcher_text or "не обещание результата" in matcher_text,"automatic-result boundary copy missing")
req('fetch("/api/route"' in matcher_js_text and 'fetch("/api/lead"' in matcher_js_text,"static matcher API bindings missing")
req("OPENROUTER_API_KEY" not in matcher_js_text,"OpenRouter key marker must never reach client JS")
req("localStorage" not in matcher_js_text and "sessionStorage" not in matcher_js_text,"static matcher must not persist user input")
for page in matcher_pages:
    text=page.read_text(encoding="utf-8")
    req('src="/matcher-v2.js"' in text,f"{page.name}: matcher-v2.js missing")
    req('id="matcher-goal"' in text and 'id="matcher-run"' in text,f"{page.name}: v2 goal/run controls missing")
    req("const S={audience:null" not in text,f"{page.name}: legacy inline matcher returned")

test_cmd=["node","--test","services/lead-ingress/test/route.test.mjs"]
result=subprocess.run(test_cmd,cwd=ROOT,text=True,capture_output=True)
checks+=1
if result.returncode!=0:
    errors.append("route tests failed")
    print(result.stdout+result.stderr)
else:
    tail=(result.stdout+result.stderr).strip().splitlines()
    for line in tail[-14:]: print(line)

print(f"route_service_checks={checks} projection_bytes={projection.stat().st_size if projection.exists() else 0}")
if errors:
    print("ROUTE_SERVICE_CONTRACT_FAIL")
    for error in errors: print("FAIL:",error)
    raise SystemExit(1)
print("ROUTE_SERVICE_CONTRACT_PASS")
