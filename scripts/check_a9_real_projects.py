#!/usr/bin/env python3
from pathlib import Path
import json
import json, sys

ROOT=Path(__file__).resolve().parents[1]
E32 = json.loads((ROOT / "deploy/live/_release.json").read_text(encoding="utf-8")).get("release_id")  in {'E3_2_RU_GLOSSARY_R1','E3_4_AI_SAFETY_AUDIENCE_R1','E3_5_HEADING_STRUCTURE_R1'}
LIVE=ROOT/"deploy/live"
errors=[]; checks=0

def req(ok,msg):
    global checks
    checks+=1
    if not ok: errors.append(msg)

component=(ROOT/"components/RealProjectGallery.tsx").read_text(encoding="utf-8")
ru_page=(ROOT/"app/(ru)/projects/page.tsx").read_text(encoding="utf-8")
en_page=(ROOT/"app/(en)/en/projects/page.tsx").read_text(encoding="utf-8")
ru=(LIVE/"projects.html").read_text(encoding="utf-8")
en=(LIVE/"en/projects.html").read_text(encoding="utf-8")
manifest=json.loads((LIVE/"_release.json").read_text(encoding="utf-8"))

projects=[
    ("VisionAssist","https://github.com/bitmaster162/VisionAssist"),
    ("ContinuityOS","https://github.com/bitmaster162/continuityos"),
    ("BitEvo Agent Authority","https://github.com/bitmaster162/agent-authority"),
    ("BitEvo Agent Site","https://github.com/bitmaster162/bitevo-agent-site"),
    ("TRIAXIS","https://github.com/bitmaster162/TRIAXIS"),
]
for title,url in projects:
    req(component.count(title)>=2,f"source missing localized project {title}")
    req(component.count(url)==2,f"source repo URL count drift {url}")
    for label,text in [("RU static",ru),("EN static",en)]:
        req(title in text,f"{label}: missing {title}")
        req(text.count(f'href="{url}"')==1,f"{label}: repo link count drift {url}")

req('"use client"' not in component,"real project gallery must stay server-rendered")
for forbidden in ["fetch(","localStorage","sessionStorage","indexedDB"]:
    req(forbidden not in component,f"real project gallery forbidden capability {forbidden}")

for label,page in [("RU source",ru_page),("EN source",en_page)]:
    hero_marker = "РЕАЛЬНЫЕ ПРОЕКТЫ · ОТКРЫТЫЕ ИСТОЧНИКИ" if E32 and label == "RU source" else "REAL BUILDS · PUBLIC PROVENANCE"
    req(hero_marker in page,f"{label}: real-build hero marker")
    expected_boundary = "ПРИМЕРЫ РЕЗУЛЬТАТОВ · НЕ ОТЗЫВЫ" if E32 and label == "RU source" else "EXAMPLE OUTPUTS · NOT TESTIMONIALS / 9 EXAMPLES"
    req(expected_boundary in page,f"{label}: example boundary marker")
    req("RealProjectGallery" in page,f"{label}: real gallery mount")

for label,text in [("RU static",ru),("EN static",en)]:
    req(text.count("data-real-project>")==5,f"{label}: real project cards != 5")
    req(text.count("data-real-projects")==1,f"{label}: real project collection != 1")
    req(text.count("data-project-tags=")==9,f"{label}: example cards must remain 9")
    req(text.count("data-project-filter=")==5,f"{label}: example filters must remain 5")
    req(text.count('target="_blank" rel="noopener noreferrer">GitHub ↗</a>')>=5,f"{label}: safe repo links")
    expected_boundary = "ПРИМЕРЫ РЕЗУЛЬТАТОВ · НЕ ОТЗЫВЫ" if E32 and label == "RU static" else "EXAMPLE OUTPUTS · NOT TESTIMONIALS / 9 EXAMPLES"
    req(expected_boundary in text,f"{label}: example boundary missing")

for marker in [
    "README не заявляет calibration",
    "Demo доказывает bounded persistence",
    "Не выдаёт trust/safety score",
    "can_trade=false",
    "это не production gateway",
    "no calibration, human-AI uplift",
    "bounded persistence across a fresh process",
    "does not issue a trust/safety score",
    "capital_permission=DENY",
    "not a production gateway",
]:
    req(marker in component,f"source boundary marker missing {marker!r}")

req("не работы учеников и не клиентские кейсы" in ru_page,"RU source must separate mentor builds from student/client work")
req("not student work or client case studies" in en_page,"EN source must separate mentor builds from student/client work")
req("не работы учеников и не клиентские кейсы" in ru,"RU static must separate mentor builds from student/client work")
req("not student work or client case studies" in en,"EN static must separate mentor builds from student/client work")

req(manifest.get("release_id") in {"A9_REAL_PROJECTS_R1","N25_CERTIFICATE_RECORD_R1","E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1","E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1","E3_5_HEADING_STRUCTURE_R1"},"A9 release identity")
req(manifest.get("file_count")==(96 if manifest.get("release_id") in {"N25_CERTIFICATE_RECORD_R1","E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1","E3_3_H1_ACTION_R1","E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1","E3_5_HEADING_STRUCTURE_R1"} else 94),"A9 static file_count")
print(f"A9_REAL_PROJECTS_CHECK checks={checks} real_projects=5 example_projects=9 public_repo_links=5")
if errors:
    print("A9_REAL_PROJECTS_FAIL")
    for e in errors: print("FAIL:",e)
    raise SystemExit(1)
print("A9_REAL_PROJECTS_PASS")
