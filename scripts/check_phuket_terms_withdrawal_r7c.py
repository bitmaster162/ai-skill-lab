#!/usr/bin/env python3
"""Scoped R7C public copy withdrawal check; no merge/deploy authority."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
MAIN = "61eaecd472dff022ec0efaf88bb80cb0b3bdd4c5"
MAIN_TREE = "d42560ff981288098e7b2bbf7398478d338dc79b"
OLD_MANIFEST_SHA = "a8166f8a45f17df8b7359dfb62bba467c6061f61cab1db164183216d31c42bb6"
RELEASE = "PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015"
PATCH = "PHUKET_UNIVERSE_U3_R7C_TERMS_WITHDRAWAL_20261015"
NOTES = {
    "phuket-universe.html": "Условия размещения обсуждаем индивидуально — напишите нам.",
    "en/phuket-universe.html": "Listing terms are discussed individually — write to us.",
}
BLOCK = re.compile(rb'<details class="pu-agency-terms" id="agency-pilot-terms" data-agency-terms-version="pilot-r1">.*?</details>', re.S)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def must(ok: bool, why: str):
    if not ok:
        raise ValueError("R7C_TERMS_HOTFIX_FAIL " + why)

def baseline(rel: str) -> bytes:
    p = subprocess.run(["git", "-C", str(ROOT), "show", MAIN + ":" + rel],
                       capture_output=True, timeout=45)
    must(p.returncode == 0, "baseline_blob_missing:" + rel)
    return p.stdout

def active() -> bool:
    m = json.loads((LIVE / "_release.json").read_text(encoding="utf-8"))
    return m.get("release_id") == RELEASE and m.get("patch_id") == PATCH

def check_release() -> dict:
    tree = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", MAIN + "^{tree}"],
                                   text=True, timeout=20).strip()
    must(tree == MAIN_TREE, "remote_baseline_tree_changed")
    old_manifest = baseline("deploy/live/_release.json")
    must(sha(old_manifest) == OLD_MANIFEST_SHA, "old_manifest_sha")
    before = json.loads(old_manifest)
    raw = (LIVE / "_release.json").read_bytes()
    now = json.loads(raw)
    must(now.get("release_id") == RELEASE and now.get("patch_id") == PATCH
         and now.get("parent_manifest_sha256") == OLD_MANIFEST_SHA, "version_lineage")
    must(now.get("schema") == "ai-skill-lab.static-release.v1"
         and now.get("file_count") == before.get("file_count") == 107,
         "manifest_schema_or_file_count")
    old_rows = {r["path"]: r for r in before["files"]}
    new_rows = {r["path"]: r for r in now["files"]}
    must(len(old_rows) == len(new_rows) == 107 and set(old_rows) == set(new_rows),
         "asset_set_drift")
    observed = {}
    for path in sorted(LIVE.rglob("*")):
        must(not path.is_symlink(), "symlink:" + str(path))
        if path.is_file() and path.name != "_release.json":
            rel = path.relative_to(LIVE).as_posix()
            payload = path.read_bytes()
            observed[rel] = {"size": len(payload), "sha256": sha(payload)}
            if rel not in NOTES:
                must(observed[rel] == {"size": old_rows[rel]["size"],
                                      "sha256": old_rows[rel]["sha256"]},
                     "unexpected_asset_change:" + rel)
    must(observed == {k: {"size": v["size"], "sha256": v["sha256"]}
                      for k, v in new_rows.items()}, "manifest_asset_mismatch")
    changed = sorted(k for k in observed if observed[k] != {
        "size": old_rows[k]["size"], "sha256": old_rows[k]["sha256"]})
    must(changed == sorted(NOTES), "exactly_two_html_changes")
    for rel, note in NOTES.items():
        old_page = baseline("deploy/live/" + rel)
        must(len(BLOCK.findall(old_page)) == 1, "old_details_cardinality:" + rel)
        expected = BLOCK.sub(lambda x: (
            '<p class="pu-agency-terms" id="agency-listing-terms">' + note + "</p>"
        ).encode("utf-8"), old_page, count=1)
        actual = (LIVE / rel).read_bytes()
        must(actual == expected, "html_not_exact_replacement:" + rel)
        must(actual.count(note.encode("utf-8")) == 1, "approved_note_cardinality:" + rel)
        must(b'id="agency-pilot-terms"' not in actual
             and b'data-agency-terms-version="pilot-r1"' not in actual,
             "old_pilot_block_still_visible:" + rel)
    combined = "".join(f"{k}\t{v['size']}\t{v['sha256']}\n"
                       for k, v in sorted(observed.items())).encode("utf-8")
    must(now.get("payload_sha256") == sha(combined), "manifest_payload_digest")
    source = (ROOT / "components" / "phuketUniverseAgencyTerms.ts").read_text("utf-8")
    must(all(note in source for note in NOTES.values()), "source_copy_parity")
    must("import terms from" not in source and "id=\"agency-listing-terms\"" in source
         and "fetch(" not in source, "source_contract_regression")
    dormant = (LIVE / "phuket-universe-events.js").read_bytes()
    must(b"const ENABLED = false;" in dormant, "universe_event_authority_change")
    return {"status": "LOCAL_PASS", "base": MAIN, "patch": PATCH,
            "files": len(observed), "changed_html": changed,
            "payload_sha256": sha(combined), "manifest_sha256": sha(raw),
            "universe_events_enabled": False, "production_authority": False}

if __name__ == "__main__":
    print(json.dumps(check_release(), ensure_ascii=False, sort_keys=True))
