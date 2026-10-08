#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
errors=[]; checks=0
def req(cond,msg):
    global checks
    checks+=1
    if not cond: errors.append(msg)
def read(rel): return (ROOT/rel).read_text(encoding="utf-8")

source=read("components/PromptAuditor.tsx")
home=read("components/workshop/WorkshopHome.tsx")
route=read("services/lead-ingress/api/route.js")
tests=read("services/lead-ingress/test/route.test.mjs")
client=read("deploy/live/prompt-auditor.js")
ru=read("deploy/live/index.html"); en=read("deploy/live/en.html")
ru_priv=read("deploy/live/privacy.html"); en_priv=read("deploy/live/en/privacy.html")
manifest=json.loads(read("deploy/live/_release.json"))

for marker in ['10-балльной шкале','10-point scale','fetch("/api/route"','mode: "prompt_audit"','maxLength={2000}','result.score}/10','result.improved','result.explanation']:
    req(marker in source,f"source missing {marker}")
req("localStorage" not in source and "sessionStorage" not in source and "indexedDB" not in source,"source must not persist prompt")
req('<PromptAuditor locale={locale}/>' in home or '<PromptAuditor locale={locale} />' in home,"homepage source must mount PromptAuditor")
for marker in ["validatePromptAuditInput","validatePromptAuditResult","promptForAudit","callPromptAuditor",'parsed?.mode === "prompt_audit"',"prompt_audit_complete"]:
    req(marker in route,f"route missing {marker}")
handle=route[route.index("export async function handleRoute"):]
req(handle.index("if (hasSecret(joined))") < handle.index("checkRouteRate(request, cfg, fetchImpl)",handle.index("const auditMode")),"secret check must precede A8 rate gate")
req(handle.index("checkRouteRate(request, cfg, fetchImpl)",handle.index("const auditMode")) < handle.index("callPromptAuditor(cfg, input, fetchImpl)"),"rate gate must precede A8 model call")
req('score < 1 || value.score > 10' in route,"score must be bounded 1..10")
audit_block=handle[handle.index("if (auditMode)"):handle.index("const table = commercialPackages")]
req("fallbackResult" not in audit_block,"Prompt Auditor must not fabricate deterministic model score")
for marker in ["prompt auditor returns a validated 10-point AI assessment","prompt auditor blocks secret-like input","prompt auditor fails closed","prompt auditor primary 401 may use","prompt auditor enforces locale and bounded prompt length"]:
    req(marker in tests,f"route tests missing {marker}")
for text,label,locale in [(ru,"ru","ru"),(en,"en","en")]:
    req(text.count("data-prompt-auditor")==1,f"{label}: one Prompt Auditor")
    req(f'data-locale="{locale}"' in text,f"{label}: locale binding")
    req(text.count('src="/prompt-auditor.js"')==1,f"{label}: runtime binding")
    req('maxlength="2000"' in text,f"{label}: input cap")
    req("/10" in text and "Prompt Auditor" in text,f"{label}: visible score/demo contract")
req('fetch("/api/route"' in client and 'mode:"prompt_audit"' in client,"static runtime API contract")
req("localStorage" not in client and "sessionStorage" not in client and "indexedDB" not in client,"static runtime must not persist prompt")
req("innerHTML" not in client and "textContent" in client,"static output must use textContent")
req("OPENROUTER_API_KEY" not in client,"server key marker must not reach client")
for text,label,markers in [
    (ru_priv,"ru privacy",["текст промпта из Prompt Auditor","Для AI-подбора или Prompt Auditor","текст Prompt Auditor"]),
    (en_priv,"en privacy",["prompt text from Prompt Auditor","For AI routing or Prompt Auditor","Prompt Auditor text"]),
]:
    for marker in markers: req(marker in text,f"{label}: missing {marker}")
req(manifest.get("release_id") in {"A8_PROMPT_AUDITOR_R1","A9_REAL_PROJECTS_R1","N25_CERTIFICATE_RECORD_R1","E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1"},"A8 release identity")
req(manifest.get("file_count")==(96 if manifest.get("release_id") in {"N25_CERTIFICATE_RECORD_R1","E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1"} else 94),"A8 release file_count")
req(sum(1 for x in manifest.get("files",[]) if x.get("path")=="prompt-auditor.js")==1,"manifest must list prompt-auditor.js once")
print(f"a8_prompt_auditor_checks={checks}")
if errors:
    print("A8_PROMPT_AUDITOR_CHECK_FAIL")
    for e in errors: print("FAIL:",e)
    raise SystemExit(1)
print("A8_PROMPT_AUDITOR_CHECK_PASS")
