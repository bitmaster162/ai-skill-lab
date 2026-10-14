#!/usr/bin/env python3
"""Create-only R2 candidate: omit the owner-approved RU/EN terms placeholders.

The sealed R1 candidate, original mockup, source pages and deploy/live are not
modified. This is not agency terms approval, release approval or deployment.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
import prepare_phuket_universe_static_r1 as previous

ROOT = previous.ROOT
ORIGIN = previous.ORIGIN
ROUTES = previous.ROUTES
need = previous.need
safe_path = previous.safe_path
RELEASE = "PHUKET_UNIVERSE_U1_STATIC_CANDIDATE_R2_20261014"
OUT = ROOT / "deploy/preview" / RELEASE
R1_MANIFEST_SHA = "2723f467629c19cb2e06ff36320eee075bb237019eefdef7279b5e97b05b9c4e"
REMOVED_PARAGRAPHS = {
    "ru": '<p class="pu-s100">Условия размещения: [УСЛОВИЯ ДЛЯ АГЕНТСТВ]</p>',
    "en": '<p class="pu-s100">Listing terms: [TERMS FOR AGENCIES]</p>',
}


def sealed_r1() -> dict[str, bytes]:
    root = ROOT / "deploy/preview" / previous.RELEASE
    need(root.is_dir() and not root.is_symlink(), "Sealed R1 unavailable")
    raw = (root / "_release.json").read_bytes()
    need(previous.sha(raw) == R1_MANIFEST_SHA, "R1 manifest drift")
    result = {}
    for file in root.rglob("*"):
        need(not file.is_symlink(), "Symlink in R1")
        if file.is_file():
            name = file.relative_to(root).as_posix()
            need(safe_path(name), "Unsafe R1 path")
            result[name] = file.read_bytes()
    payload = {n: b for n, b in result.items() if n != "_release.json"}
    previous.verify_manifest(payload, raw)
    return result


def remove_terms_paragraph(text: str, locale: str) -> str:
    need(locale in REMOVED_PARAGRAPHS, "Unknown locale")
    paragraph = REMOVED_PARAGRAPHS[locale]
    need(text.count(paragraph) == 1, "Terms paragraph missing or duplicated")
    return text.replace(paragraph, "", 1)


def render() -> tuple[dict[str, bytes], dict]:
    original, old_stats = previous.render()
    need(original == sealed_r1(), "Reconstructed R1 differs from sealed candidate")
    files = original.copy()
    changed = set()
    for locale, route in ROUTES.items():
        name = route.lstrip("/") + ".html"
        before = original[name].decode("utf-8")
        after = remove_terms_paragraph(before, locale)
        files[name] = after.encode("utf-8")
        changed.add(name)
        parsed = previous.Page(after)
        need([a.get("id") for t, a in parsed.tags if t == "section"] ==
             ["top", "orbit", "homes", "agencies"], "Section structure changed")
        need(sum(t == "svg" for t, _ in parsed.tags) == 8, "SVG structure changed")
        need('mailto:robert@aiskillab.work' in after, "Agency contact removed")
        need("[TERMS FOR AGENCIES]" not in after and
             "[УСЛОВИЯ ДЛЯ АГЕНТСТВ]" not in after, "Terms placeholder survived")
    need({n for n in original if files[n] != original[n]} == changed,
         "Unexpected payload changes before manifest")
    payload = {n: b for n, b in files.items() if n != "_release.json"}
    entries = previous.file_index(payload)
    manifest = {
        "schema": "ai-skill-lab.static-release.v1", "release_id": RELEASE,
        "file_count": len(entries), "payload_sha256": previous.payload_digest(entries),
        "files": entries,
    }
    raw = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
    previous.verify_manifest(payload, raw)
    files["_release.json"] = raw
    stats = dict(old_stats)
    font_bytes = sum(len(b) for n, b in payload.items() if n.endswith(".woff2"))
    non_font_bytes = sum(len(b) for n, b in payload.items() if not n.endswith(".woff2"))
    stats.update({
        "release_id": RELEASE, "previous_release_id": previous.RELEASE,
        "previous_manifest_sha256": R1_MANIFEST_SHA,
        "manifest_sha256": previous.sha(raw),
        "payload_sha256": manifest["payload_sha256"],
        "payload_bytes": font_bytes + non_font_bytes,
        "non_font_bytes": non_font_bytes,
        "payload_delta_bytes": font_bytes + non_font_bytes -
            sum(map(len, previous.parent_payload().values())),
        "r1_payload_files_unchanged": len(payload) - len(changed),
        "r1_payload_files_changed": sorted(changed),
        "terms_placeholders_removed": ["ru", "en"],
        "agency_terms_status": "NOT_DEFINED_RESEARCH_REQUIRED",
        "public_agency_terms_published": False,
        "publication_holds": [h for h in old_stats["publication_holds"]
            if h != "SOURCE_AGENCY_TERMS_PLACEHOLDER_UNRESOLVED"],
    })
    return files, stats


def write_candidate(files: dict[str, bytes]) -> None:
    need(not previous.git("status", "--porcelain=v1"), "Commit and clean before seal")
    need(not OUT.exists(), "R2 exists; no overwrite or silent reseal")
    need(OUT.parent.resolve().is_relative_to(ROOT.resolve()), "Unsafe output root")
    need(all(safe_path(n) for n in files), "Unsafe output path")
    OUT.mkdir(parents=True, exist_ok=False)
    for name in sorted(files, key=lambda n: (n == "_release.json", n)):
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(files[name])
    actual = {p.relative_to(OUT).as_posix(): p.read_bytes()
              for p in OUT.rglob("*") if p.is_file()}
    need(actual == files, "R2 write mismatch; STOP without retry")
    need(sealed_r1()["_release.json"] ==
         (ROOT / "deploy/preview" / previous.RELEASE / "_release.json").read_bytes(),
         "R1 changed during R2 write")
    print("R2_CANDIDATE_WRITTEN", str(OUT), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-candidate", action="store_true")
    args = parser.parse_args()
    files, stats = render()
    if args.write_candidate:
        write_candidate(files)
    print(json.dumps(stats, ensure_ascii=False, sort_keys=True, indent=2), flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
