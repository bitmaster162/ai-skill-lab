#!/usr/bin/env python3
"""Local-only sitemap freshness successor to the exact R3.1 post-R7C candidate.

Only 54 non-Universe lastmod values advance to 2026-10-16. The two Universe
routes stay at 2026-10-15. No content, JS, authority, deploy or API change.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

import build_site_r31_post_r7c as prior

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"
BASE = "cae4b9e319a395512639dffdb09a897d215c0181"
BASE_TREE = "7e80c54e20800a30d9314030f6369ebe88881179"
PARENT_MANIFEST_SHA = "c9c1ffa4a227a4ed324901c7bb6019e16dcf28722fc70c72e70badfb22752505"
GRANDPARENT_MANIFEST_SHA = "b10b2ad45184e2f19a329dbe22b7e2c18fef0c075f13a31a435abdf83167adc3"
RELEASE = "PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015"
PATCH = "SITE_FORM_METADATA_R31_POST_R7C_SITEMAP_20261016_LOCAL_R2"
NORMAL_DAY = "2026-10-16"
UNIVERSE_DAY = "2026-10-15"
UNIVERSE_PATHS = frozenset(("/phuket-universe", "/en/phuket-universe"))
# Constants are populated only from the independently reproduced first candidate.
EXPECTED_MANIFEST_SHA = "fc57c61c7ac502644665f7cc06152f43fb0b5d7f67827eb6fd4b12aadfc83f37"
EXPECTED_PAYLOAD_SHA = "9a8e8b41646a2dcb07ef7fa849088666c07891a41e5050d56bcfc99a1ff03b0e"
XML_ROW = re.compile(r"<url><loc>https://aiskillab\.work([^<]*)</loc><lastmod>(\d{4}-\d{2}-\d{2})</lastmod>(?:<changefreq>monthly</changefreq><priority>0\.8</priority>)?</url>")


def need(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("R31_SITEMAP_R2_HOLD " + reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(*args: str) -> bytes:
    r = subprocess.run(["git", "--no-optional-locks", "-C", str(ROOT), *args],
                       capture_output=True, timeout=40)
    need(r.returncode == 0, "read_git:" + " ".join(args[:2]))
    return r.stdout


def verify_source() -> None:
    need(git("rev-parse", BASE + "^{tree}").decode().strip() == BASE_TREE,
         "exact_baseline_tree")
    old = git("show", BASE + ":app/sitemap.ts").replace(b"\r\n", b"\n")
    before = b'const lastModified = "2026-10-15";'
    after = b'const lastModified = "2026-10-16";'
    need(old.count(before) == 1 and old.count(after) == 0, "old_sitemap_source_pin")
    observed = (ROOT / "app/sitemap.ts").read_bytes().replace(b"\r\n", b"\n")
    need(observed == old.replace(before, after, 1), "only_approved_source_date")
    need(observed.count(b'universeRoutes.includes(route) ? "2026-10-15" : lastModified') == 1,
         "universe_date_source_preserved")


def parent_files() -> tuple[dict[str, bytes], dict]:
    # This reproduces all 108 parent assets from immutable R7C + reviewed R3.1.
    files, result = prior.render()
    need(result["manifest_sha256"] == PARENT_MANIFEST_SHA,
         "reproduced_r31_parent_manifest")
    recorded = git("show", BASE + ":deploy/live/_release.json")
    need(sha(recorded) == PARENT_MANIFEST_SHA and files["_release.json"] == recorded,
         "published_parent_manifest_pin")
    parent = json.loads(recorded)
    need(parent.get("patch_id") == prior.PATCH
         and parent.get("parent_manifest_sha256") == GRANDPARENT_MANIFEST_SHA
         and parent.get("release_id") == RELEASE and parent.get("file_count") == 108,
         "parent_grandparent_lineage")
    need(files["sitemap.xml"] == git("show", BASE + ":deploy/live/sitemap.xml"),
         "parent_xml_pin")
    need(b"const ENABLED = false;" in files["phuket-universe-events.js"],
         "universe_event_authority")
    return files, parent


def update_sitemap(raw: bytes) -> bytes:
    original = raw.decode("utf-8")
    all_rows = XML_ROW.findall(original)
    need(len(all_rows) == 56 and len({p for p, _ in all_rows}) == 56,
         "exact_public_route_count_56")
    need(sum(p in UNIVERSE_PATHS for p, _ in all_rows) == 2,
         "exact_universe_pair")
    need(all(day == UNIVERSE_DAY for _, day in all_rows), "parent_sitemap_day_15")
    changed = []
    def replace(row: re.Match[str]) -> str:
        path, day = row.group(1), row.group(2)
        if path in UNIVERSE_PATHS:
            return row.group(0)
        changed.append(path)
        return row.group(0).replace("<lastmod>" + day + "</lastmod>",
                                    "<lastmod>" + NORMAL_DAY + "</lastmod>", 1)
    updated = XML_ROW.sub(replace, original)
    need(len(changed) == 54 and len(set(changed)) == 54,
         "exactly_54_normal_routes_advance")
    now = XML_ROW.findall(updated)
    need(len(now) == 56
         and all(day == (UNIVERSE_DAY if path in UNIVERSE_PATHS else NORMAL_DAY)
                 for path, day in now), "exact_date_scopes")
    need(updated.count("<lastmod>" + NORMAL_DAY + "</lastmod>") == 54,
         "new_normal_date_cardinality")
    need(updated.count("<lastmod>" + UNIVERSE_DAY + "</lastmod>") == 2,
         "universe_day_cardinality")
    return updated.encode("utf-8")


def render() -> tuple[dict[str, bytes], dict]:
    verify_source()
    original, parent = parent_files()
    files = dict(original)
    files["sitemap.xml"] = update_sitemap(original["sitemap.xml"])
    need({path for path in original if original[path] != files[path]} ==
         {"sitemap.xml"}, "exact_one_parent_asset_delta")
    records = [{"path": path, "size": len(raw), "sha256": sha(raw)}
               for path, raw in sorted(files.items()) if path != "_release.json"]
    need(len(records) == 108, "asset_inventory_108")
    payload_sha = sha("".join(
        f"{row['path']}\t{row['size']}\t{row['sha256']}\n" for row in records
    ).encode("utf-8"))
    manifest = dict(parent)
    manifest.update({"patch_id": PATCH,
                     "parent_manifest_sha256": PARENT_MANIFEST_SHA,
                     "files": records, "file_count": 108,
                     "payload_sha256": payload_sha})
    files["_release.json"] = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    new_manifest_sha = sha(files["_release.json"])
    if EXPECTED_MANIFEST_SHA and EXPECTED_PAYLOAD_SHA:
        need(new_manifest_sha == EXPECTED_MANIFEST_SHA
             and payload_sha == EXPECTED_PAYLOAD_SHA, "independently_pinned_output")
    return files, {
        "base": BASE, "source_tree": BASE_TREE, "patch": PATCH, "release": RELEASE,
        "manifest_sha256": new_manifest_sha, "payload_sha256": payload_sha,
        "parent_manifest_sha256": PARENT_MANIFEST_SHA,
        "grandparent_manifest_sha256": GRANDPARENT_MANIFEST_SHA,
        "files": 108, "routes": 56, "changed_assets": ["sitemap.xml"],
        "normal_lastmod": NORMAL_DAY, "normal_routes": 54,
        "universe_lastmod": UNIVERSE_DAY, "universe_routes": 2,
        "production_authority": False, "universe_events_enabled": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-local-once", action="store_true")
    args = parser.parse_args()
    files, result = render()
    if args.apply_local_once:
        need(sha((LIVE / "_release.json").read_bytes()) == PARENT_MANIFEST_SHA,
             "apply_only_against_original_v1")
        need(not git("diff", "--name-only", "HEAD", "--", "deploy/live").strip(),
             "preexisting_deploy_tree_changes")
        for rel in ("sitemap.xml", "_release.json"):
            (LIVE / rel).write_bytes(files[rel])
        result["written_local"] = True
    else:
        result["written_local"] = False
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
