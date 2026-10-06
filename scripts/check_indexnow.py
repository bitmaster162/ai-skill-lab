#!/usr/bin/env python3
from __future__ import annotations
import ast
import importlib.util
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
KEY="98ac1c70-f355-43f0-84f5-57cbf4c68e18"
errors=[];checks=0

def req(cond,msg):
    global checks
    checks+=1
    if not cond:errors.append(msg)

for rel in [f"deploy/live/{KEY}.txt",f"public/{KEY}.txt"]:
    p=ROOT/rel
    req(p.is_file(),f"{rel}: missing")
    if p.is_file():
        req(p.read_text(encoding="utf-8").strip()==KEY,f"{rel}: content mismatch")

sitemap=(ROOT/"deploy/live/sitemap.xml").read_text(encoding="utf-8")
req(KEY not in sitemap,"IndexNow key file must not be in sitemap")

script=ROOT/"scripts/indexnow_notify.py"
req(script.is_file(),"indexnow_notify.py missing")
if script.is_file():
    text=script.read_text(encoding="utf-8")
    ast.parse(text)
    for marker in [
        'ENDPOINT="https://api.indexnow.org/indexnow"',
        'HOST="aiskillab.work"',
        'KEY_LOCATION=f"{ORIGIN}/{KEY_FILE_NAME}"',
        'status not in (200,202)',
        'wait_for_live',
        'verify_live_key',
        '"urlList":urls',
        '["git","diff","--name-only",before,head,"--"]',
    ]:
        req(marker in text,f"indexnow_notify.py missing {marker}")

wf=(ROOT/".github/workflows/indexnow.yml").read_text(encoding="utf-8")
for marker in [
    "push:",
    "branches:",
    "- main",
    "fetch-depth: 0",
    "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
    "python scripts/indexnow_notify.py",
    "--wait-for-live",
    "INDEXNOW_BEFORE: ${{ github.event.before }}",
    "INDEXNOW_HEAD: ${{ github.sha }}",
]:
    req(marker in wf,f"workflow missing {marker}")
req(wf.count("python scripts/indexnow_notify.py")==1,"workflow command must appear once")
req("actions/checkout@v" not in wf,"IndexNow checkout must be pinned to a full commit SHA")
req("pull_request:" not in wf,"IndexNow must not run on pull_request")
req("workflow_dispatch:" not in wf,"IndexNow has no manual mutation path")

spec=importlib.util.spec_from_file_location("indexnow_notify",script)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
urls=mod.sitemap_urls()
req(len(urls)==52,"sitemap URL authority must be 52")
req(mod.urls_for_changes([f"deploy/live/{KEY}.txt"])==urls,"first key deployment must submit all sitemap URLs")
req(mod.urls_for_changes(["deploy/live/pricing.html"])==["https://aiskillab.work/pricing"],"single route mapping")
req(mod.urls_for_changes(["deploy/live/en/pricing.html"])==["https://aiskillab.work/en/pricing"],"EN route mapping")
req(mod.urls_for_changes(["deploy/live/404.html"])==[],"404 must never be submitted")
req(mod.urls_for_changes(["deploy/live/workshop.css"])==urls,"global CSS change must submit all sitemap URLs")
req(mod.urls_for_changes([".github/workflows/indexnow.yml"])==urls,"IndexNow workflow recovery must submit all sitemap URLs")
req(mod.urls_for_changes(["scripts/indexnow_notify.py"])==urls,"IndexNow notifier recovery must submit all sitemap URLs")

print(f"INDEXNOW_CONTRACT_CHECKS={checks} sitemap_urls={len(urls)}")
if errors:
    print("INDEXNOW_CONTRACT_FAIL")
    for e in errors:print("-",e)
    sys.exit(1)
print("INDEXNOW_CONTRACT_PASS")
