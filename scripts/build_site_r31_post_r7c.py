#!/usr/bin/env python3
"""Exact local-only selective R3.1 patch atop sealed R7C (no publication authority).

Read pinned Git blobs; replace only 3 EN SEO fields, 2 form shells, old form JS,
and the corresponding CSP hash. Preserve all other R7C assets and sitemap dates.
"""
from __future__ import annotations

import argparse
import hashlib
import base64
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
from site_inline_script_csp_r3 import inline_script_hashes

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"
BASE = "866ad2d2fd0cbd9b3ccedec65d55ed60a3c3a642"
BASE_TREE = "114cccff48005950f0bf6665a629e7163b402d3f"
SOURCE = "0f1422eb67aac4855c7d5561e92832fd859cf4e1"
SOURCE_TREE = "33e66cc859847339cf8494a9154ed6ca82c694cc"
PARENT_MANIFEST_SHA = "b10b2ad45184e2f19a329dbe22b7e2c18fef0c075f13a31a435abdf83167adc3"
EXPECTED_MANIFEST_SHA = "c9c1ffa4a227a4ed324901c7bb6019e16dcf28722fc70c72e70badfb22752505"
EXPECTED_PAYLOAD_SHA = "33fce831c34403b7236c8267ea4adf37c57d3412ce796a8858cbf8ce28debf61"
RELEASE = "PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015"
PATCH = "SITE_FORM_METADATA_R31_POST_R7C_LOCAL_20261016"
NOTE = {
    "ru": ("Форма пока не готова к отправке. Можно связаться напрямую.",
           "Прямые контакты: Telegram, WhatsApp, LINE или email"),
    "en": ("The form is not ready yet. You can contact us directly.",
           "Direct contacts: Telegram, WhatsApp, LINE or email"),
}
SEO = (
    ("app/(en)/en/page.tsx", "en.html",
     "AI Skill Lab · Phuket — practical AI learning and workflow pilots",
     "AI Skill Lab · Phuket — AI learning and workflow pilots"),
    ("app/(en)/en/start/page.tsx", "en/start.html",
     "Start — pick a track and a first task | AI Skill Lab · Phuket",
     "Start — pick a track and first task | AI Skill Lab · Phuket"),
    ("guides/aiskillab/ai-safety-for-kids.en.md", "en/guides/ai-safety-for-kids.html",
     "Age rules for ChatGPT, Gemini, Claude, Suno, Replit and GitHub, five questions to ask of any AI tool, and how ChatGPT parental controls work. Checked 1 October 2026.",
     "Age rules for ChatGPT, Gemini, Claude, Suno, Replit and GitHub, five questions for any AI tool, and ChatGPT parental controls. Checked 1 October 2026."),
)
COPIED_SOURCE = {
    "components/LeadForm.tsx",
    "app/(en)/en/page.tsx",
    "app/(en)/en/start/page.tsx",
    "guides/aiskillab/ai-safety-for-kids.en.md",
    "public/lead-form-runtime.js",
    "scripts/site_inline_script_csp_r3.py",
}
ALLOWED_MODIFIED = frozenset({
    "en.html", "en/start.html", "en/guides/ai-safety-for-kids.html",
    "start.html", "start-brief.js", "vercel.json",
})


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("R31_POST_R7C_HOLD " + message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(*args: str, timeout: int = 25) -> bytes:
    r = subprocess.run(["git", "--no-optional-locks", "-C", str(ROOT), *args],
                       capture_output=True, timeout=timeout)
    need(r.returncode == 0, "git_read_failed:" + " ".join(args[:2]))
    return r.stdout


def verify_git() -> None:
    need(git("rev-parse", BASE + "^{tree}").decode().strip() == BASE_TREE, "base_tree")
    need(git("rev-parse", SOURCE + "^{tree}").decode().strip() == SOURCE_TREE, "source_tree")
    for path in COPIED_SOURCE:
        ours = (ROOT / path).read_bytes()
        theirs = git("show", SOURCE + ":" + path)
        need(ours.replace(b"\r\n", b"\n") == theirs.replace(b"\r\n", b"\n"),
             "reviewed_source_pin:" + path)


def parent_files() -> tuple[dict[str, bytes], dict]:
    archive = git("archive", "--format=tar", BASE, "deploy/live", timeout=40)
    need(len(archive) < 5 * 1024 * 1024, "parent_archive_size")
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for entry in tar:
            if not entry.isfile():
                continue
            need(entry.name.startswith("deploy/live/") and
                 ".." not in entry.name.split("/"), "parent_member_path")
            handle = tar.extractfile(entry)
            need(handle is not None, "missing_tar_member")
            files[entry.name.removeprefix("deploy/live/")] = handle.read()
    oldraw = files.pop("_release.json")
    need(sha(oldraw) == PARENT_MANIFEST_SHA, "parent_manifest_sha")
    m = json.loads(oldraw)
    need(m.get("patch_id") == "PHUKET_UNIVERSE_U3_R7C_TERMS_WITHDRAWAL_20261015"
         and m.get("release_id") == RELEASE and m.get("file_count") == 107,
         "parent_r7c_identity")
    pins = {f["path"]: f for f in m["files"]}
    need(set(pins) == set(files) and len(files) == 107, "parent_inventory")
    for path, data in files.items():
        need(len(data) == pins[path]["size"] and sha(data) == pins[path]["sha256"],
             "parent_member_pin:" + path)
    for rel, text in (
        ("phuket-universe.html", "Условия размещения обсуждаем индивидуально — напишите нам."),
        ("en/phuket-universe.html", "Listing terms are discussed individually — write to us."),
    ):
        need(files[rel].count(text.encode("utf-8")) == 1 and
             b'id="agency-pilot-terms"' not in files[rel], "R7C_public_copy")
    need(b"const ENABLED = false;" in files["phuket-universe-events.js"],
         "E38_must_remain_dormant")
    return files, m


def inline_hashes(files: dict[str, bytes]) -> set[str]:
    hashes: set[str] = set()
    for name, payload in files.items():
        if name.endswith(".html"):
            hashes.update(inline_script_hashes(payload.decode("utf-8")))
    return hashes


def render() -> tuple[dict[str, bytes], dict]:
    verify_git()
    files, parent = parent_files()
    old_hashes = inline_hashes(files)
    for source, rel, before, after in SEO:
        source_bytes = (ROOT / source).read_text(encoding="utf-8")
        need(source_bytes.count(after) >= 1, "metadata_source:" + source)
        page = files[rel].decode("utf-8")
        need(page.count(before) in (3, 4), "metadata_cardinality:" + rel)
        files[rel] = page.replace(before, after).encode("utf-8")
    for locale, rel in (("ru", "start.html"), ("en", "en/start.html")):
        page = files[rel].decode("utf-8")
        marker = '<form class="leadForm" id="application-form">'
        old_note = re.findall(r'<noscript><p class="formNote">[^<]*</p></noscript>', page)
        need(page.count(marker) == 1 and len(old_note) == 1, "form_boundary:" + rel)
        note, direct = NOTE[locale]
        page = page.replace(old_note[0], "", 1).replace(
            marker, marker[:-1] + ' data-lead-state="unready">' +
            '<p class="formNote" data-lead-readiness role="status">' + note + '</p>' +
            '<p class="formNote" data-lead-direct-contact><a href="#contact-channels">' +
            direct + '</a></p>', 1)
        submit = '<button class="workshopButton workshopButtonPrimary formSubmit" type="submit">'
        need(page.count(submit) == 1, "form_button_boundary:" + rel)
        page = page.replace(submit, submit[:-1] + " disabled>", 1)
        script = re.findall(r'<script\b[^>]*src="/start-brief.js"[^>]*></script>', page)
        need(len(script) == 1, "form_script_boundary:" + rel)
        page = page.replace(script[0], script[0] +
                            '<script src="/lead-form-runtime.js" defer></script>', 1)
        files[rel] = page.encode("utf-8")
    split = b'(function(){"use strict";const form=document.querySelector("#application-form");'
    need(files["start-brief.js"].count(split) == 1, "old_submission_handler_unique")
    files["start-brief.js"] = files["start-brief.js"].split(split, 1)[0]
    need(files["start-brief.js"] == git("show", SOURCE + ":deploy/live/start-brief.js"),
         "reviewed_start_brief")
    files["lead-form-runtime.js"] = (ROOT / "public/lead-form-runtime.js").read_bytes()
    need(files["lead-form-runtime.js"] == git("show", SOURCE + ":deploy/live/lead-form-runtime.js"),
         "reviewed_runtime")
    new_hashes = inline_hashes(files)
    removed, added = old_hashes - new_hashes, new_hashes - old_hashes
    need(len(removed) == len(added) == 1, "exact_one_csp_hash_replacement")
    text = files["vercel.json"].decode("utf-8")
    old, new = next(iter(removed)), next(iter(added))
    need(text.count(old) == 1 and "'unsafe-inline'" not in text, "csp_old_hash_unique")
    files["vercel.json"] = text.replace(old, new, 1).encode("utf-8")
    csp = json.loads(files["vercel.json"])["headers"][0]["headers"]
    policy = next(h["value"] for h in csp if h["key"] == "Content-Security-Policy")
    need("form-action 'none'" in policy and all(h in policy for h in new_hashes),
         "csp_policy_or_coverage")
    # Preserve all non-scoped files, including R7C, all 56 routes, and Oct-15 sitemap.
    previous, _ = parent_files()
    modified = {name for name in previous if previous[name] != files[name]}
    need(modified == ALLOWED_MODIFIED and set(files) - set(previous) == {"lead-form-runtime.js"},
         "selected_static_scope")
    need(files["sitemap.xml"] == previous["sitemap.xml"], "sitemap_date_drift")
    records = [{"path": k, "size": len(v), "sha256": sha(v)}
               for k, v in sorted(files.items())]
    digest = sha("".join(f"{v['path']}\t{v['size']}\t{v['sha256']}\n"
                        for v in records).encode("utf-8"))
    manifest = dict(parent)
    manifest.update({
        "patch_id": PATCH,
        "parent_manifest_sha256": PARENT_MANIFEST_SHA,
        "files": records,
        "file_count": len(records),
        "payload_sha256": digest,
    })
    need(len(records) == 108, "new_inventory_exact_108")
    files["_release.json"] = (json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    need(digest == EXPECTED_PAYLOAD_SHA and sha(files["_release.json"]) == EXPECTED_MANIFEST_SHA,
         "independent_candidate_payload_or_manifest_pin")
    return files, {"scope": sorted(modified), "added": ["lead-form-runtime.js"],
                   "payload_sha256": digest, "manifest_sha256": sha(files["_release.json"]),
                   "assets": len(records), "routes": 56, "authority": False,
                   "parent_manifest_sha256": PARENT_MANIFEST_SHA}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-local-once", action="store_true")
    args = parser.parse_args()
    files, report = render()
    if args.apply_local_once:
        current_manifest = (LIVE / "_release.json").read_bytes()
        need(sha(current_manifest) == PARENT_MANIFEST_SHA, "apply_requires_r7c_current")
        tracked = git("diff", "--name-only", "HEAD", "--", "deploy/live")
        need(not tracked.strip(), "local_live_already_modified")
        missing = LIVE / "lead-form-runtime.js"
        need(not missing.exists(), "asset_already_exists")
        for name in sorted(ALLOWED_MODIFIED | {"lead-form-runtime.js", "_release.json"}):
            p = LIVE / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(files[name])
        report["written_local"] = True
    else:
        report["written_local"] = False
    print(json.dumps(report, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
