#!/usr/bin/env python3
from pathlib import Path
import json
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
errors=[]; checks=0

def req(ok,msg):
    global checks
    checks+=1
    if not ok: errors.append(msg)

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.h1=0; self.forms=0; self.links=[]; self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="h1": self.h1+=1
        if tag=="form": self.forms+=1
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag=="script" and a.get("src"): self.scripts.append(a["src"])

src_ru=(ROOT/"app/(ru)/certificate/page.tsx").read_text(encoding="utf-8")
src_en=(ROOT/"app/(en)/en/certificate/page.tsx").read_text(encoding="utf-8")
ru=(LIVE/"certificate.html").read_text(encoding="utf-8")
en=(LIVE/"en/certificate.html").read_text(encoding="utf-8")
method_ru=(LIVE/"method.html").read_text(encoding="utf-8")
method_en=(LIVE/"en/method.html").read_text(encoding="utf-8")
readme=(ROOT/"README.md").read_text(encoding="utf-8")
sitemap=(LIVE/"sitemap.xml").read_text(encoding="utf-8")
llms=(LIVE/"llms.txt").read_text(encoding="utf-8")
manifest=json.loads((LIVE/"_release.json").read_text(encoding="utf-8"))

for label,src in [("RU source",src_ru),("EN source",src_en)]:
    req(''"use client"'' not in src,f"{label}: must stay server-rendered")
    for bad in ["fetch(","localStorage","sessionStorage","indexedDB","document.cookie","WebSocket(","<form","<input"]:
        req(bad not in src,f"{label}: forbidden runtime/data primitive {bad}")

for label,text,canon,alt in [
    ("RU static",ru,"https://aiskillab.work/certificate","https://aiskillab.work/en/certificate"),
    ("EN static",en,"https://aiskillab.work/en/certificate","https://aiskillab.work/certificate"),
]:
    p=P(); p.feed(text)
    req(p.h1==1,f"{label}: exactly one H1")
    req(p.forms==0,f"{label}: no form")
    req(p.scripts==["/lab-command.js","/_vercel/insights/script.js"],f"{label}: no certificate-specific runtime")
    req(f'<link rel="canonical" href="{canon}">' in text,f"{label}: canonical")
    req(f'href="{alt}"' in text,f"{label}: language alternate/link")
    req(text.count("TEMPLATE · NOT ISSUED")>=2,f"{label}: template-not-issued marker")
    req("N25 · COMPLETION RECORD · CONSENT-BOUND" in text,f"{label}: N25 marker")

for marker in [
    "Сертификат не является главным результатом программы",
    "Это не аккредитация",
    "Никакой student record не выпущен",
    "отдельного согласия на публикацию",
    "имя, возраст, фото, школу, контакт, username, account/repository links",
]:
    req(marker in ru,f"RU contract missing {marker!r}")
for marker in [
    "certificate is not the primary learning outcome",
    "This is not accreditation",
    "No student record has been issued here",
    "separate consent to publication",
    "name, age, photo, school, contact, username, account/repository links",
]:
    req(marker in en,f"EN contract missing {marker!r}")

for text,label in [(ru,"RU"),(en,"EN")]:
    low=text.lower()
    for forbidden in ["certificate_id","certificate-id","verification_id","verification-id","issued_to","date_of_birth","student_email","student_phone"]:
        req(forbidden not in low,f"{label}: invented issued-record field {forbidden}")

req(method_ru.count('href="/certificate"')==1,"RU method: one certificate inlink")
req(method_en.count('href="/en/certificate"')==1,"EN method: one certificate inlink")
req(sitemap.count("<loc>https://aiskillab.work/certificate</loc>")==1,"sitemap RU certificate")
req(sitemap.count("<loc>https://aiskillab.work/en/certificate</loc>")==1,"sitemap EN certificate")
req("/certificate/" not in sitemap and "/en/certificate/" not in sitemap,"no per-student public certificate routes")
req(llms.count("[RU](https://aiskillab.work/certificate) [EN](https://aiskillab.work/en/certificate)")==1,"llms certificate pair")
req("/certificate" in readme and "/en/certificate" in readme,"README route inventory")
req("consent-bound completion-record policy/template only" in readme,"README N25 truth")
req("issued certificates" in readme,"README no-fabricated-issued-certificate discipline")

req(manifest.get("release_id") in {"N25_CERTIFICATE_RECORD_R1","E3_8_LEAD_EVENTS_R1","E3_1_RU_SEO_R1"},"N25-or-successor release identity")
req(manifest.get("file_count")==96,"N25 static file_count 96")
listed={x.get("path") for x in manifest.get("files",[])}
req({"certificate.html","en/certificate.html"}<=listed,"manifest certificate pair")
req(len([p for p in LIVE.rglob("*.html") if p.name!="404.html"])==52,"52 public HTML routes")
req(len(list(LIVE.rglob("*.html")))==53,"53 HTML including 404")

print(f"N25_CERTIFICATE_CHECK checks={checks} public_routes=52 issued_records=0 minor_public_pii=0")
if errors:
    print("N25_CERTIFICATE_FAIL")
    for e in errors: print("FAIL:",e)
    raise SystemExit(1)
print("N25_CERTIFICATE_PASS")
