#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
errors=[]; checks=0
EVENTS=["lead_submit_ok","lead_submit_error","cal_click","telegram_click","whatsapp_click","line_click","email_click"]
RU="Сайт ведёт first-party счётчик событий заявки и переходов по каналам связи без персональных данных и cookie: сохраняются только тип события, страница, язык и дневной счётчик; имена, контакты и текст формы туда не передаются."
EN="The site uses a first-party counter for application and contact-channel events without personal data or cookies: only the event type, page, locale and daily count are stored; names, contact details and form text are not sent to that counter."

def req(ok,msg):
 global checks
 checks+=1
 if not ok: errors.append(msg)
def read(rel): return (ROOT/rel).read_text(encoding="utf-8")

tracker=read("components/PublicEventTracker.tsx")
ingress=read("services/lead-ingress/api/event.js")
worker=read("services/lead-receiver-cloudflare/src/index.js")
static_runtime=read("deploy/live/lab-command.js")
start=read("deploy/live/start-brief.js")
lead=read("components/LeadForm.tsx")
intro=read("components/IntroCallCta.tsx")
for event in EVENTS:
 for label,text in [("source tracker",tracker),("ingress",ingress),("worker",worker)]:
  req(event in text,f"{label}: missing {event}")
for marker in [
 'fetch("/api/event"',
 'credentials:"omit"',
 'body:JSON.stringify({event:e,page:p,locale:l})',
 '"cal.com":"cal"',
 '"t.me":"telegram"',
 '"wa.me":"whatsapp"',
 '"line.me":"line"',
 'a.protocol=="mailto:"?"email"',
 'n+"_click"',
 'addEventListener("asl:lead-event"',
]:
 req(marker in static_runtime,f"static runtime marker {marker}")
for text,label in [(tracker,"source tracker"),(static_runtime,"static runtime")]:
 for forbidden in ["document.cookie","localStorage","sessionStorage","sendBeacon(","window.va","intro_call_click"]:
  req(forbidden not in text,f"{label}: forbidden {forbidden}")
req('credentials: "omit"' in tracker,"source tracker credentials omit")
req('credentials:"omit"' in static_runtime,"static tracker credentials omit")
req('body: JSON.stringify({ event, page: pagePath(), locale: pageLocale() })' in tracker,"source client payload exact")
for event in ["lead_submit_ok","lead_submit_error"]:
 req(f'event: "{event}"' in lead,f"source form dispatch {event}")
 req(f'event:"{event}"' in start,f"static form dispatch {event}")
req("window.va" not in intro and "intro_call_click" not in intro,"old Vercel custom event source removed")
req("window.va" not in static_runtime and "intro_call_click" not in static_runtime,"old Vercel custom event static removed")
for rel,phrase in [
 ("app/(ru)/privacy/page.tsx",RU),("app/(en)/en/privacy/page.tsx",EN),
 ("deploy/live/privacy.html",RU),("deploy/live/en/privacy.html",EN),
]:
 req(read(rel).count(phrase)==1,f"{rel}: privacy sentence exact once")
manifest=json.loads(read("deploy/live/_release.json"))
req(manifest.get("release_id")in {"E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1","E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1"},"E3.8 release identity")
req(manifest.get("file_count")==96,"E3.8 static file_count 96")
ingress_project=json.loads(read("services/lead-ingress/vercel.json"))
req(
 ingress_project.get("git",{}).get("deploymentEnabled")
 == {"agent/**":False,"agent/ingress-*":True,"local/e3-8-lead-events-r1-20261007":True},
 "E3.8 ingress preview branch allow exact",
)
req(ingress_project.get("functions",{}).get("api/event.js")=={"maxDuration":10},"E3.8 ingress event function exact")
cfg=json.loads(read("deploy/live/vercel.json"))
event_rewrites=[x for x in cfg.get("rewrites",[]) if x.get("source")=="/api/event"]
req(event_rewrites==[{"source":"/api/event","destination":"https://ai-skill-lab-ingress.vercel.app/api/event"}],"public event rewrite exact")
req(not any(x.get("source")=="/api/event-report" for x in cfg.get("rewrites",[])),"report must not be public rewrite")
ingress_cfg=json.loads(read("services/lead-ingress/vercel.json"))
req(ingress_cfg.get("functions",{}).get("api/event.js")=={"maxDuration":10},"ingress event function config")
for marker in ['const PUBLIC_EVENT_PATH = "/e3/event";','const PUBLIC_EVENT_REPORT_PATH = "/e3/event-report";',"PUBLIC_EVENT_UPSERT_SQL","PUBLIC_EVENT_REPORT_SQL","handlePublicEvent","handlePublicEventReport"]:
 req(marker in worker,f"worker missing {marker}")
req("public_event_daily_e38" in read("schema/public_event_daily_e38.sql"),"D1 event schema")
req(" name text" not in read("schema/public_event_daily_e38.sql").lower(),"D1 schema must not store name")
req("contact" not in read("schema/public_event_daily_e38.sql").lower(),"D1 schema must not store contact")
for rel in ["app/(ru)/layout.tsx","app/(en)/layout.tsx"]:
 req('PublicEventTracker' in read(rel),f"{rel}: source tracker mount")
workflow=read(".github/workflows/static-qa.yml"); preflight=read("scripts/preflight_release.py")
for cmd in [
 "python scripts/check_e3_8_lead_events.py",
 "node scripts/check_e3_8_event_runtime.mjs",
 "python scripts/check_e3_8_event_schema.py",
 "node --test services/lead-ingress/test/event.test.mjs",
 "node --test services/lead-receiver-cloudflare/test/public-event.test.mjs",
]:
 req(workflow.count(cmd)==1,f"workflow count {cmd}")
 needle=cmd.replace("python ","").replace("node ","").replace("--test ","")
 # preflight uses argument arrays; require script/test path once.
 path=cmd.split()[-1]
 req(preflight.count(path)==1,f"preflight count {path}")
print(f"e3_8_lead_event_checks={checks} events={len(EVENTS)} client_fields=3 pii_fields=0")
if errors:
 print("E3_8_LEAD_EVENTS_FAIL"); [print("FAIL:",e) for e in errors]; sys.exit(1)
print("E3_8_LEAD_EVENTS_PASS")
