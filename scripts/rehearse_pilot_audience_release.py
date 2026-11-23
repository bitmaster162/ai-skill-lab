"""Compare the complete preflight on the published bilingual pilot and its reviewed R4.

The report is diagnostic. Its release preflight status stays failed whenever any
gate fails, including a gate that already failed on the published snapshot.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from build_business_pilot_audience_preview import MANIFEST, R3_MANIFEST_SHA256, digest, require
from preflight_release import CHECKS
from test_pilot_snapshot_routes import test_snapshot
from prepare_phuket_universe_static_r1 import verify_manifest

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_BUILDER = "da921cb58fe7cd2b03265d3681508d1be432509e"
PUBLISHED = "c70f71cc58d4977b82600adf5b12db773606542573d28ad309cde4ad39d94799"
R3_BUILDER = "f39fff8cba3e5bb59b4503721972421169685c37"
CANDIDATE = "ed753e4324d6fce0f1d258d8bad422730271f46a865934d32c4abab9267a6430"
CHANGED = {"business.html", "en/business.html", "lead-form-runtime.js"}
BUILDER = "scripts/build_business_pilot_audience_preview.py"
ADAPTER = "scripts/static-adapters/pilot-business-audience.js"


def snapshot(site: Path, expected_digest: str) -> dict[str, bytes]:
    paths = list(site.rglob("*"))
    require(not site.is_symlink() and not any(p.is_symlink() for p in paths), "symlink in site")
    assets = {p.relative_to(site).as_posix(): p.read_bytes() for p in paths if p.is_file()}
    manifest = assets.pop(MANIFEST)
    require(digest(manifest) == expected_digest, "unrecognized release manifest")
    verified = verify_manifest(assets, manifest)
    if expected_digest == CANDIDATE:
        require(verified["parent_manifest_sha256"] == R3_MANIFEST_SHA256, "unexpected R4 parent")
    return assets


def build_historical(work: Path, original: Path, commit: str, label: str) -> Path:
    builder_root = work / (label + "-builder")
    for name in (BUILDER, ADAPTER):
        target = builder_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT))
    output = work / label
    subprocess.run([sys.executable, "-B", str(builder_root / BUILDER), str(output),
                    "--parent-root", str(original)], cwd=ROOT, check=True)
    return output


def compare_scope(published: Path, previous: Path, candidate: Path) -> list[str]:
    old = snapshot(published, PUBLISHED)
    new = snapshot(candidate, CANDIDATE)
    r3 = snapshot(previous, R3_MANIFEST_SHA256)
    require(old.keys() == r3.keys() == new.keys(), "asset inventory changed")
    require({name for name in r3 if r3[name] != new[name]} == {"lead-form-runtime.js"},
            "R4 must change only the form runtime relative to R3")
    changed = {name for name in old if old[name] != new[name]}
    require(changed == CHANGED, f"unexpected changes: {sorted(changed)}")
    return sorted(changed)


def run_preflight(work: Path, source: Path, expected: str, revision: str) -> dict:
    subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(work)], check=True)
    subprocess.run(["git", "checkout", "--quiet", "--detach", revision], cwd=work, check=True)
    (work / "node_modules").symlink_to(ROOT / "node_modules", target_is_directory=True)
    site = work / "deploy/live"
    shutil.rmtree(site)  # Only the private clone inside TemporaryDirectory is changed.
    shutil.copytree(source, site)
    snapshot(site, expected)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    results = {}
    for name, cmd in [*CHECKS, ("git_diff_check", ["git", "diff", "--check"])]:
        proc = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        results[name] = {"exit_code": proc.returncode}
        if proc.returncode:
            results[name]["output"] = (proc.stdout + proc.stderr).strip()[-8000:]
        print(f"{source.name} {name}: {proc.returncode}", flush=True)
    snapshot(site, expected)
    return {"manifest_sha256": expected, "status": "FAIL" if failures(results) else "PASS", "checks": results}


def failures(results: dict) -> set[str]:
    return {name for name, result in results.items() if result["exit_code"] != 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, type=Path, help="original sealed static builder input")
    parser.add_argument("--candidate", required=True, type=Path, help="assembled R4 static directory")
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    require((ROOT / "node_modules/eslint/bin/eslint.js").is_file(), "locked npm dependencies required")
    with TemporaryDirectory(prefix="pilot-preflight-") as tmp:
        work = Path(tmp)
        original = args.original.resolve()
        published = build_historical(work, original, PUBLISHED_BUILDER, "published")
        previous = build_historical(work, original, R3_BUILDER, "r3")
        changed = compare_scope(published, previous, args.candidate)
        for site in (published, args.candidate):
            test_snapshot(site)
        before = run_preflight(work / "control", published, PUBLISHED, revision)
        after = run_preflight(work / "review", args.candidate.resolve(), CANDIDATE, revision)
    old = failures(before["checks"])
    new = failures(after["checks"])
    summary = {"tested_per_snapshot": len(after["checks"]), "previously_passing_now_failing": sorted(new - old),
               "failing_on_both": sorted(new & old), "now_passing": sorted(old - new)}
    receipt = {"schema": "ai-skill-lab.pilot-preflight-comparison.v1", "git": revision,
               "changed_assets": changed, "previous_candidate": R3_MANIFEST_SHA256, "published": before, "candidate": after, "summary": summary}
    args.receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    return int(bool(new - old))


if __name__ == "__main__":
    raise SystemExit(main())
