#!/usr/bin/env python3
"""Local-only metadata preview and intercepted browser checks; never a release gate.

Usage: python -B scripts/verify_site_metadata_preview_r1.py --preview <NEW_DIR>
       --receipt <JSON> [--browser <CHROME_EXECUTABLE>]
The sealed deploy/live directory is read-only. No HTTP request is continued from
browser fixtures: all page traffic is fulfilled from local files, mocked, or aborted.
This script does not publish, install packages, change accounts, or contact a backend.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "df78cffa5d68cbacbcc578dd1035248ae15a364c"
ORIGIN = "https://aiskillab.work"
RELEASE_ID = "SITE_METADATA_LOCAL_PREVIEW_R2_20261014"
CHANGES = [
    ("app/(en)/en/page.tsx", "en.html", "title", 2,
     "AI Skill Lab \u00b7 Phuket \u2014 practical AI learning and workflow pilots",
     "AI Skill Lab \u00b7 Phuket \u2014 AI learning and workflow pilots"),
    ("app/(en)/en/start/page.tsx", "en/start.html", "title", 2,
     "Start \u2014 pick a track and a first task | AI Skill Lab \u00b7 Phuket",
     "Start \u2014 pick a track and first task | AI Skill Lab \u00b7 Phuket"),
    ("guides/aiskillab/ai-safety-for-kids.en.md", "en/guides/ai-safety-for-kids.html", "description", 1,
     "Age rules for ChatGPT, Gemini, Claude, Suno, Replit and GitHub, five questions to ask of any AI tool, and how ChatGPT parental controls work. Checked 1 October 2026.",
     "Age rules for ChatGPT, Gemini, Claude, Suno, Replit and GitHub, five questions for any AI tool, and ChatGPT parental controls. Checked 1 October 2026."),
]

def check(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git(*args: str) -> bytes:
    p = subprocess.run(["git", "--no-optional-locks", "-C", str(ROOT), *args],
                       capture_output=True, timeout=20)
    check(p.returncode == 0, "Git read failed: " + p.stderr.decode(errors="replace")[-240:])
    return p.stdout

class Html(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.h1 = 0
        self.meta: dict[str, str] = {}
        self.canonical: list[str] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = dict(attrs)
        if tag == "title": self.in_title = True
        if tag == "h1": self.h1 += 1
        if tag == "meta": self.meta[str(d.get("name") or d.get("property"))] = str(d.get("content") or "")
        if tag == "link" and d.get("rel") == "canonical": self.canonical.append(str(d.get("href")))
    def handle_endtag(self, tag: str) -> None:
        if tag == "title": self.in_title = False
    def handle_data(self, text: str) -> None:
        if self.in_title: self.title += text

def html(path: Path) -> Html:
    p = Html(); p.feed(path.read_text(encoding="utf-8")); return p

def script_hashes(folder: Path) -> set[str]:
    out: set[str] = set()
    for path in folder.rglob("*.html"):
        for attrs, text in re.findall(r"<script\b([^>]*)>([\s\S]*?)</script>", path.read_text(encoding="utf-8")):
            if not re.search(r"\bsrc\s*=", attrs) and text.strip():
                out.add("'sha256-" + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode() + "'")
    return out

def verify_manifest(folder: Path) -> dict:
    m = json.loads((folder / "_release.json").read_bytes())
    names = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file() and p.name != "_release.json"}
    check(names == {f["path"] for f in m["files"]}, "Manifest inventory mismatch")
    check(len(names) == m["file_count"] == 98, "Manifest count mismatch")
    for f in m["files"]:
        b = (folder / f["path"]).read_bytes()
        check(len(b) == f["size"] and sha(b) == f["sha256"], "Manifest member drift: " + f["path"])
    aggregate = "".join(f"{f['path']}\t{f['size']}\t{f['sha256']}\n" for f in m["files"]).encode()
    check(sha(aggregate) == m["payload_sha256"], "Manifest aggregate mismatch")
    return m

def create_and_check_preview(target: Path) -> dict:
    sealed = ROOT / "deploy/live"
    old_manifest = verify_manifest(sealed)
    check(not git("diff", BASE, "--", "deploy/live"), "Sealed release changed")
    check(not target.exists(), "Preview exists; use a new destination, do not overwrite")
    check(ROOT not in target.parents and target != ROOT, "Preview must be outside source repository")
    source_changes = []
    for source, static, field, count, before, after in CHANGES:
        original = git("show", BASE + ":" + source).decode()
        current = (ROOT / source).read_text(encoding="utf-8")
        check(original.count(before) == count, "Source occurrence mismatch: " + source)
        check(current == original.replace(before, after), "Out-of-scope source diff: " + source)
        source_changes.append({"source": source, "route": "/" + static.removesuffix(".html"),
                               "field": field, "before": before, "after": after,
                               "length_before": len(before), "length_after": len(after)})
    shutil.copytree(sealed, target)
    for source, static, field, count, before, after in CHANGES:
        p = target / static
        raw = p.read_text(encoding="utf-8")
        check(raw.count(before) in (3, 4), "Unexpected static metadata count")
        p.write_bytes(raw.replace(before, after).encode())
        check(raw.split("<body", 1)[1] == p.read_text(encoding="utf-8").split("<body", 1)[1], "Visible body changed")
        parsed = html(p)
        value = parsed.title if field == "title" else parsed.meta["description"]
        check(value == after, "HTML value mismatch")
        check(parsed.meta["og:" + field] == after and parsed.meta["twitter:" + field] == after, "Social metadata mismatch")
    # The guide description also occurs in JSON-LD: update its CSP hash, not the policy.
    old_hashes, new_hashes = script_hashes(sealed), script_hashes(target)
    removed, added = old_hashes - new_hashes, new_hashes - old_hashes
    check(len(removed) == len(added) == 1, "Expected exactly one JSON-LD hash change")
    old_hash, new_hash = next(iter(removed)), next(iter(added))
    cfg = target / "vercel.json"
    text = cfg.read_text(encoding="utf-8")
    check(text.count(old_hash) == 1, "Old JSON-LD hash not unique in CSP")
    cfg.write_bytes(text.replace(old_hash, new_hash).encode())
    cfg_data = json.loads(cfg.read_bytes())
    headers = next(x["headers"] for x in cfg_data["headers"] if x["source"] == "/(.*)")
    csp = next(x["value"] for x in headers if x["key"].lower() == "content-security-policy")
    check(all(h in csp for h in new_hashes), "Uncovered inline script")
    check("form-action 'none'" in csp and "'unsafe-inline'" not in csp, "CSP policy weakened")
    members = []
    for p in sorted((p for p in target.rglob("*") if p.is_file() and p.name != "_release.json"), key=lambda p:p.relative_to(target).as_posix()):
        b = p.read_bytes(); members.append({"path":p.relative_to(target).as_posix(),"size":len(b),"sha256":sha(b)})
    aggregate = "".join(f"{f['path']}\t{f['size']}\t{f['sha256']}\n" for f in members).encode()
    manifest = {"schema":"ai-skill-lab.static-release.v1","release_id":RELEASE_ID,
                "file_count":len(members),"files":members,"payload_sha256":sha(aggregate)}
    (target / "_release.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    verify_manifest(target)
    urls = [x.text for x in ET.parse(target / "sitemap.xml").getroot().findall("{*}url/{*}loc")]
    check(len(urls) == 54, "Expected 54 sitemap routes")
    for url in urls:
        path = urlsplit(str(url)).path
        p = target / ("index.html" if path == "/" else path.strip("/") + ".html")
        x = html(p)
        check(x.h1 == 1 and x.canonical == [url], "H1/canonical failure: " + path)
        check(0 < len(x.title) <= 60 and 0 < len(x.meta.get("description", "")) <= 160, "Editorial length failure: " + path)
    differing = sorted(p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file() and p.read_bytes() != (sealed / p.relative_to(target)).read_bytes())
    check(differing == sorted([x[1] for x in CHANGES] + ["vercel.json","_release.json"]), "Unexpected preview change")
    return {"source_changes":source_changes,"routes_checked":54,"manifest_members_checked":98,
            "preview_differing_files":differing,"csp_hash_replaced":{"before":old_hash,"after":new_hash},
            "parent_release":old_manifest["release_id"],"preview_release":RELEASE_ID,
            "payload_sha256":manifest["payload_sha256"],"sitemap_dates_changed":False,
            "all_visible_bodies_preserved":True,"sealed_release_unchanged":True,
            "full_next_build_or_release_admission":False}

def browser_checks(executable: str) -> dict:
    from playwright.sync_api import sync_playwright
    sealed = ROOT / "deploy/live"
    config = json.loads((sealed / "vercel.json").read_bytes())
    headers = {x["key"]:x["value"] for rule in config["headers"] if rule["source"] == "/(.*)" for x in rule["headers"]}
    cases = []; start = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=executable, headless=True, timeout=12000,
            args=["--disable-background-networking","--disable-component-update","--no-first-run"])
        try:
            for locale in ("ru", "en"):
                route_path = "/start" if locale == "ru" else "/en/start"
                for viewport in (dict(width=1440,height=900),dict(width=390,height=844)):
                    for mode in ("javascript_disabled", "handler_missing"):
                        for trigger in ("click", "enter"):
                            check(time.monotonic()-start < 100, "Browser test time budget")
                            ctx = browser.new_context(java_script_enabled=(mode!="javascript_disabled"),
                                service_workers="block", offline=True, viewport=viewport)
                            ctx.set_default_timeout(3500)
                            records = []; errors = []; continued = 0
                            def intercept(rt):
                                req = rt.request; u = urlsplit(req.url)
                                records.append({"method":req.method,"path":u.path,"query":u.query,
                                                "has_synthetic": "ASL_SYNTHETIC" in unquote(req.url) or "ASL_SYNTHETIC" in (req.post_data or "")})
                                if u.netloc != "aiskillab.work" or req.method!="GET" or u.query:
                                    rt.abort(); return
                                if u.path.startswith("/api/") or u.path.startswith("/_vercel/") or (mode=="handler_missing" and u.path=="/start-brief.js"):
                                    rt.abort(); return
                                rel = "index.html" if u.path=="/" else u.path.lstrip("/")
                                if "." not in Path(rel).name: rel += ".html"
                                dest=(sealed / rel).resolve()
                                if not dest.is_relative_to(sealed.resolve()) or not dest.is_file():
                                    rt.abort(); return
                                ctype=mimetypes.guess_type(dest.name)[0] or "application/octet-stream"
                                if dest.suffix==".js":ctype="application/javascript"
                                rt.fulfill(status=200,body=dest.read_bytes(),headers={**headers,"Content-Type":ctype})
                            ctx.route("**/*",intercept)
                            page=ctx.new_page()
                            page.on("console",lambda msg:errors.append(msg.text) if msg.type=="error" else None)
                            try:
                                page.goto(ORIGIN+route_path,wait_until="load",timeout=7000)
                                page.locator('form#application-form input[name="name"]').fill("ASL_SYNTHETIC_TEST")
                                page.locator('form#application-form input[name="contact"]').fill("asl-synthetic@example.invalid")
                                page.locator('form#application-form textarea[name="goal"]').fill("ASL_SYNTHETIC_NO_LIVE_REQUEST")
                                page.locator('form#application-form input[name="privacyConsent"]').check()
                                valid=page.locator("form#application-form").evaluate("f => f.checkValidity()")
                                check(valid, "Browser fixture invalid: would not exercise submission")
                                if trigger=="click":page.locator('form#application-form button[type="submit"]').click(no_wait_after=True)
                                else:page.locator('form#application-form input[name="contact"]').press("Enter", no_wait_after=True)
                                page.wait_for_timeout(150)
                                sensitive_attempts=[r for r in records if r["has_synthetic"] or r["method"]!="GET"]
                                csp_messages=[s for s in errors if "form-action" in s]
                                fallback=page.locator("noscript p.formNote")
                                fallback_visible=fallback.count()>0 and fallback.first.is_visible()
                                contact_visible=page.locator("#contact-channels").is_visible()
                                message=page.locator("[data-lead-message]").inner_text()
                                check(page.url==ORIGIN+route_path and not sensitive_attempts, "Form data request attempted")
                                check(bool(csp_messages), "No evidence of CSP blocking actual form submit")
                                check(contact_visible, "Direct contact fallback unavailable")
                                if mode=="javascript_disabled":check(fallback_visible, "No-JS guidance not visible")
                                cases.append({"locale":locale,"width":viewport["width"],"mode":mode,"trigger":trigger,
                                    "valid_form":valid,"field_request_attempts":len(sensitive_attempts),"csp_block_observed":bool(csp_messages),
                                    "url_unchanged":True,"nojs_note_visible":fallback_visible,"direct_contacts_available":contact_visible,
                                    "user_status_message":message,"external_requests_continued":continued,"status":"PASS"})
                                print(json.dumps({"browser_case":len(cases),**cases[-1]},ensure_ascii=True),flush=True)
                            finally:ctx.close()
        finally:browser.close()
    return {"cases":cases,"count":len(cases),"passed":sum(c["status"]=="PASS" for c in cases),
            "coverage":"Chromium only, exact stored production HTML/CSP, synthetic fields, all page requests intercepted locally",
            "live_backend_test":False,"user_browser_or_profile_used":False,"full_cross_browser_claim":False,
            "network_requests_continued":0,
            "remaining_ux_issue":"With JS enabled but handler missing, noscript guidance is hidden and the form may show no status message despite CSP blocking. Direct contact routes remain available."}

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preview",required=True,type=Path)
    ap.add_argument("--receipt",required=True,type=Path)
    ap.add_argument("--browser")
    args=ap.parse_args()
    check(args.receipt.parent.exists(), "Receipt directory missing")
    report={"schema":"ai-skill-lab.site-metadata-local-validation.v1","baseline":BASE,
            "production_changes":0,"release_admitted":False}
    try:
        report["metadata"]=create_and_check_preview(args.preview.resolve())
        print("METADATA_PREVIEW_PASS routes=54 members=98",flush=True)
        if args.browser:report["browser"]=browser_checks(args.browser)
        report["status"]="PASS_LOCAL_ONLY"
        return 0
    except Exception as exc:
        report["status"]="HOLD"; report["error"]=str(exc)
        raise
    finally:
        args.receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")

if __name__ == "__main__":
    raise SystemExit(main())
