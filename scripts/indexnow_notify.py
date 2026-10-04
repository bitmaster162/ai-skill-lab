#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy"/"live"
ORIGIN="https://aiskillab.work"
HOST="aiskillab.work"
ENDPOINT="https://api.indexnow.org/indexnow"
KEY_FILE_NAME="98ac1c70-f355-43f0-84f5-57cbf4c68e18.txt"
KEY_PATH=LIVE/KEY_FILE_NAME
KEY_LOCATION=f"{ORIGIN}/{KEY_FILE_NAME}"
PUBLIC_HTML_RE=re.compile(r"^deploy/live/(.+\.html)$")
GLOBAL_PUBLIC_ASSETS={
    "deploy/live/workshop.css",
    "deploy/live/lab-command.js",
    "deploy/live/project-filter.js",
    "deploy/live/proof-lab.js",
    "deploy/live/start-brief.js",
    "deploy/live/sitemap.xml",
    f"deploy/live/{KEY_FILE_NAME}",
}
INDEXNOW_CONTROL_PLANE={
    ".github/workflows/indexnow.yml",
    "scripts/indexnow_notify.py",
}

def read_key() -> str:
    key=KEY_PATH.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}",key):
        raise ValueError("IndexNow key format invalid")
    if KEY_PATH.name != key+".txt":
        raise ValueError("IndexNow key filename must match key")
    return key

def sitemap_urls() -> list[str]:
    text=(LIVE/"sitemap.xml").read_text(encoding="utf-8")
    urls=re.findall(r"<loc>(https://aiskillab\.work[^<]+)</loc>",text)
    if len(urls)!=50 or len(set(urls))!=50:
        raise ValueError(f"sitemap canonical URL authority drift count={len(urls)} unique={len(set(urls))}")
    return sorted(urls)

def changed_paths(before: str, head: str) -> list[str]:
    if not before or set(before)=={"0"}:
        return ["deploy/live/sitemap.xml"]
    cp=subprocess.run(
        ["git","diff","--name-only",before,head,"--"],
        cwd=ROOT,text=True,capture_output=True,check=True,
    )
    return [line.strip().replace("\\","/") for line in cp.stdout.splitlines() if line.strip()]

def route_url_from_html(rel: str) -> str | None:
    m=PUBLIC_HTML_RE.match(rel)
    if not m:
        return None
    name=m.group(1)
    if name=="404.html":
        return None
    if name=="index.html":
        return ORIGIN+"/"
    if name=="en.html":
        return ORIGIN+"/en"
    return ORIGIN+"/"+name[:-5]

def urls_for_changes(paths: list[str]) -> list[str]:
    authority=set(sitemap_urls())
    if any(p in GLOBAL_PUBLIC_ASSETS or p in INDEXNOW_CONTROL_PLANE for p in paths):
        return sorted(authority)
    urls=set()
    for p in paths:
        url=route_url_from_html(p)
        if url and url in authority:
            urls.add(url)
    return sorted(urls)

def local_release() -> tuple[str,str]:
    data=json.loads((LIVE/"_release.json").read_text(encoding="utf-8"))
    release=str(data.get("release_id") or "")
    payload=str(data.get("payload_sha256") or "")
    if not release or not re.fullmatch(r"[0-9a-f]{64}",payload):
        raise ValueError("local release marker incomplete")
    return release,payload

def fetch_bytes(url: str, timeout: float=20.0) -> tuple[int,bytes]:
    req=urllib.request.Request(url,headers={"User-Agent":"ai-skill-lab-indexnow-r1","Accept-Encoding":"identity"})
    with urllib.request.urlopen(req,timeout=timeout) as res:
        return int(res.status),res.read()

def wait_for_live(max_attempts: int, delay_seconds: float) -> None:
    want_release,want_payload=local_release()
    last=""
    for attempt in range(1,max_attempts+1):
        try:
            status,body=fetch_bytes(ORIGIN+"/_release.json")
            data=json.loads(body)
            live_release=str(data.get("release_id") or "")
            live_payload=str(data.get("payload_sha256") or "")
            last=f"status={status} release={live_release} payload={live_payload}"
            if status==200 and live_release==want_release and live_payload==want_payload:
                print(f"INDEXNOW_LIVE_RELEASE_READY attempt={attempt} release={want_release} payload={want_payload}")
                return
        except Exception as exc:
            last=f"{type(exc).__name__}: {exc}"
        if attempt<max_attempts:
            time.sleep(delay_seconds)
    raise RuntimeError(f"live release did not converge: {last}")

def verify_live_key(key: str) -> None:
    status,body=fetch_bytes(KEY_LOCATION)
    text=body.decode("utf-8","strict").strip()
    if status!=200 or text!=key:
        raise RuntimeError(f"live key verification failed status={status} exact={text==key}")
    print(f"INDEXNOW_KEY_LIVE status={status} location={KEY_LOCATION}")

def submit(key: str, urls: list[str]) -> int:
    body=json.dumps({
        "host":HOST,
        "key":key,
        "keyLocation":KEY_LOCATION,
        "urlList":urls,
    },separators=(",",":")).encode("utf-8")
    req=urllib.request.Request(
        ENDPOINT,data=body,method="POST",
        headers={"Content-Type":"application/json; charset=utf-8","User-Agent":"ai-skill-lab-indexnow-r1"},
    )
    try:
        with urllib.request.urlopen(req,timeout=30) as res:
            status=int(res.status)
            res.read()
    except urllib.error.HTTPError as exc:
        status=int(exc.code)
        exc.read()
    print(f"INDEXNOW_RESPONSE status={status} urls={len(urls)} endpoint={ENDPOINT}")
    if status not in (200,202):
        raise RuntimeError(f"IndexNow rejected submission: HTTP {status}")
    return status

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--before",default="")
    ap.add_argument("--head",default="HEAD")
    ap.add_argument("--wait-for-live",action="store_true")
    ap.add_argument("--max-attempts",type=int,default=60)
    ap.add_argument("--delay-seconds",type=float,default=10.0)
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()
    key=read_key()
    paths=changed_paths(args.before,args.head)
    urls=urls_for_changes(paths)
    print(f"INDEXNOW_CHANGESET paths={len(paths)} urls={len(urls)}")
    for url in urls:
        print("INDEXNOW_URL",url)
    if args.dry_run:
        print("INDEXNOW_DRY_RUN_PASS")
        return 0
    if not urls:
        print("INDEXNOW_NO_PUBLIC_URL_CHANGES")
        return 0
    if args.wait_for_live:
        wait_for_live(args.max_attempts,args.delay_seconds)
    verify_live_key(key)
    submit(key,urls)
    print("INDEXNOW_NOTIFY_PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
