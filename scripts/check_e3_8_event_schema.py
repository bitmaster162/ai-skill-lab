#!/usr/bin/env python3
from pathlib import Path
import re, sqlite3, sys

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"schema/public_event_daily_e38.sql"
WORKER=ROOT/"services/lead-receiver-cloudflare/src/index.js"
WORKFLOW=ROOT/".github/workflows/static-qa.yml"
PREFLIGHT=ROOT/"scripts/preflight_release.py"
errors=[]; checks=0

def req(ok,msg):
 global checks
 checks+=1
 if not ok: errors.append(msg)

sql=SCHEMA.read_text(encoding="utf-8")
worker=WORKER.read_text(encoding="utf-8")
for forbidden in ["name","contact","goal","cookie","ip_token","request_id","user_agent"]:
 req(re.search(r"\b"+re.escape(forbidden)+r"\b",sql,re.I) is None,f"schema contains forbidden field {forbidden}")

db=sqlite3.connect(":memory:")
db.executescript(sql)
cols=[x[1] for x in db.execute("pragma table_info(public_event_daily_e38)").fetchall()]
req(cols==["day","event_name","page","locale","count"],f"columns {cols}")
upsert="""INSERT INTO public_event_daily_e38(day,event_name,page,locale,count) VALUES(?,?,?,?,1)
ON CONFLICT(day,event_name,page,locale) DO UPDATE SET count=count+1"""
db.execute(upsert,("2026-10-07","cal_click","/pricing","en"))
db.execute(upsert,("2026-10-07","cal_click","/pricing","en"))
req(db.execute("select count from public_event_daily_e38").fetchone()[0]==2,"upsert counter")
for bad in ["other","lead_submit_okx"]:
 try:
  db.execute("insert into public_event_daily_e38 values(?,?,?,?,1)",("2026-10-07",bad,"/","en"))
  errors.append(f"invalid event accepted {bad}")
 except sqlite3.IntegrityError:
  pass
 checks+=1

req("INSERT INTO public_event_daily_e38" in worker,"worker upsert")
req("SELECT day, event_name AS event, page, locale, count" in worker,"worker report projection")
req(WORKFLOW.read_text(encoding="utf-8").count("python scripts/check_e3_8_event_schema.py")==1,"workflow schema checker once")
req(PREFLIGHT.read_text(encoding="utf-8").count("scripts/check_e3_8_event_schema.py")==1,"preflight schema checker once")
print(f"e3_8_event_schema_checks={checks} columns={len(cols)}")
if errors:
 print("E3_8_EVENT_SCHEMA_FAIL")
 for x in errors: print("FAIL:",x)
 sys.exit(1)
print("E3_8_EVENT_SCHEMA_PASS")
