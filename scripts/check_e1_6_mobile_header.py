#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/"deploy/live"
errors=[];pages=0
for p in sorted(x for x in LIVE.rglob("*.html") if x.name!="404.html"):
 rel=p.relative_to(LIVE).as_posix();h=p.read_text(encoding="utf-8");pages+=1
 if h.count('class="workshopMenuToggle"')!=1:errors.append(f"{rel}: mobile toggle count")
 if h.count('class="workshopBurger"')!=1:errors.append(f"{rel}: burger count")
 if h.count('id="workshop-nav"')!=1:errors.append(f"{rel}: workshop-nav id count")
 if 'aria-controls="workshop-nav"' not in h:errors.append(f"{rel}: aria-controls")
 if h.count('data-lab-command-open')!=1:errors.append(f"{rel}: Lab Command trigger count")
source=(ROOT/"components/workshop/WorkshopShell.tsx").read_text(encoding="utf-8")
for marker in ("styles.mobileMenuToggle","styles.burger",'id="workshop-nav"','aria-controls="workshop-nav"'):
 if marker not in source:errors.append(f"source missing {marker}")
css=(ROOT/"components/workshop/WorkshopShell.module.css").read_text(encoding="utf-8")
static=(LIVE/"workshop.css").read_text(encoding="utf-8")
for name,text in (("source css",css),("static css",static)):
 for marker in ("@media(max-width:420px)","MenuToggle:checked","pointer:coarse","labCommandTrigger" if name=="source css" else "data-lab-command-open"):
  if marker not in text:errors.append(f"{name}: missing {marker}")
print(f"E1_6_MOBILE_HEADER_STATIC pages={pages}")
if errors:
 print("E1_6_MOBILE_HEADER_FAIL");[print("-",e) for e in errors];sys.exit(1)
print("E1_6_MOBILE_HEADER_STATIC_PASS")
