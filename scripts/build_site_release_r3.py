#!/usr/bin/env python3
"""Build the exact R3 site payload into a NEW external directory, never publish.

Reads the pinned historical Git baseline and the current reviewed source. Existing
release manifests and output directories are never overwritten by this builder.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
from verify_site_metadata_preview_r1 import CHANGES
from build_site_form_preview_r1 import COPY
from site_form_metadata_r3 import RELEASE, PAYLOAD_SHA
from site_inline_script_csp_r3 import inline_script_hashes

ROOT = Path(__file__).resolve().parents[1]
PARENT_COMMIT = "df78cffa5d68cbacbcc578dd1035248ae15a364c"
PARENT_TREE = "0d8417a42df03e633ea74d98e73f9cc1f422aa76"
PARENT_MANIFEST_SHA = "1c0486827cac8fceab7c2a395d3c12a47edaac56af0ecf72459cce256429e74f"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(ROOT), *args], capture_output=True, timeout=20)
    need(result.returncode == 0, "historical Git read failed")
    return result.stdout


def parent_files() -> dict[str, bytes]:
    need(git("rev-parse", PARENT_COMMIT + "^{tree}").decode().strip() == PARENT_TREE, "parent Git tree changed")
    blob = git("archive", "--format=tar", PARENT_COMMIT, "deploy/live")
    need(len(blob) < 4 * 1024 * 1024, "unexpected parent archive size")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(blob)) as tar:
        for item in tar:
            if not item.isfile():
                continue
            need(item.name.startswith("deploy/live/") and ".." not in item.name.split("/"), "unexpected archive path")
            handle = tar.extractfile(item)
            need(handle is not None, "missing archive member")
            files[item.name.removeprefix("deploy/live/")] = handle.read()
    raw = files.pop("_release.json")
    need(sha(raw) == PARENT_MANIFEST_SHA, "parent immutable manifest changed")
    manifest = json.loads(raw)
    need(set(files) == {f["path"] for f in manifest["files"]}, "parent inventory changed")
    for f in manifest["files"]:
        data = files[f["path"]]
        need((len(data), sha(data)) == (f["size"], f["sha256"]), "parent asset changed")
    return files


def inline_hashes(files):
    hashes = set()
    for name, raw in files.items():
        if not name.endswith(".html"):
            continue
        hashes.update(inline_script_hashes(raw.decode("utf-8")))
    return hashes


def render() -> dict[str, bytes]:
    files = parent_files()
    old_hashes = inline_hashes(files)
    for source, rel, field, count, before, after in CHANGES:
        need(after in (ROOT / source).read_text(encoding="utf-8"), "metadata source mismatch")
        raw = files[rel].decode()
        need(raw.count(before) in (3, 4), "metadata replacement not exact")
        files[rel] = raw.replace(before, after).encode()
    for locale, rel in (("ru", "start.html"), ("en", "en/start.html")):
        raw = files[rel].decode()
        form = '<form class="leadForm" id="application-form">'
        notes = re.findall(r'<noscript><p class="formNote">[^<]*</p></noscript>', raw)
        need(raw.count(form) == 1 and len(notes) == 1, "form/fallback boundary drift")
        note, direct = COPY[locale]
        raw = raw.replace(notes[0], "", 1).replace(form, form[:-1] + ' data-lead-state="unready">' +
            '<p class="formNote" data-lead-readiness role="status">' + note + '</p>' +
            '<p class="formNote" data-lead-direct-contact><a href="#contact-channels">' + direct + '</a></p>', 1)
        submit = '<button class="workshopButton workshopButtonPrimary formSubmit" type="submit">'
        need(raw.count(submit) == 1, "submit boundary drift")
        raw = raw.replace(submit, submit[:-1] + " disabled>", 1)
        tags = re.findall(r'<script\b[^>]*src="/start-brief.js"[^>]*></script>', raw)
        need(len(tags) == 1, "brief script boundary drift")
        files[rel] = raw.replace(tags[0], tags[0] + '<script src="/lead-form-runtime.js" defer></script>', 1).encode()
    split = b'(function(){"use strict";const form=document.querySelector("#application-form");'
    need(files["start-brief.js"].count(split) == 1, "legacy handler boundary drift")
    files["start-brief.js"] = files["start-brief.js"].split(split, 1)[0]
    files["lead-form-runtime.js"] = (ROOT / "public/lead-form-runtime.js").read_bytes()
    for route, stamp in {'/en': '2026-10-14', '/en/guides/ai-safety-for-kids': '2026-10-14', '/en/start': '2026-10-14', '/start': '2026-10-14'}.items():
        xml = files["sitemap.xml"].decode("utf-8")
        pattern = r'(<loc>https://aiskillab\.work' + re.escape(route) + r'</loc>\s*<lastmod>)2026-10-11(</lastmod>)'
        xml, count = re.subn(pattern, lambda m: m.group(1) + stamp + m.group(2), xml)
        need(count == 1, "exact changed-route sitemap date")
        files["sitemap.xml"] = xml.encode("utf-8")
    new_hashes = inline_hashes(files)
    removed, added = old_hashes - new_hashes, new_hashes - old_hashes
    need(len(removed) == len(added) == 1, "unexpected inline-script change")
    text = files["vercel.json"].decode()
    need(text.count(next(iter(removed))) == 1, "old CSP hash not unique")
    files["vercel.json"] = text.replace(next(iter(removed)), next(iter(added)), 1).encode()
    records = [{"path": k, "size": len(v), "sha256": sha(v)} for k, v in sorted(files.items())]
    aggregate = "".join(f"{f['path']}\t{f['size']}\t{f['sha256']}\n" for f in records).encode()
    need(len(records) == 99 and sha(aggregate) == PAYLOAD_SHA, "candidate payload differs from exact R3.1 patch")
    manifest = {"schema": "ai-skill-lab.static-release.v1", "release_id": RELEASE,
                "file_count": 99, "files": records, "payload_sha256": PAYLOAD_SHA}
    files["_release.json"] = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    need(not out.exists() and out != ROOT and ROOT not in out.parents, "output must be NEW and outside repository")
    files = render()
    out.mkdir(parents=True)
    for name, data in files.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps({"release_id": RELEASE, "payload_sha256": PAYLOAD_SHA,
                     "manifest_sha256": sha(files["_release.json"]), "files_including_manifest": len(files), "published": False}))


if __name__ == "__main__":
    main()
