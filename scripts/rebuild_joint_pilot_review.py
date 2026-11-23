"""Rebuild the externally reviewed joint R4 without modifying its three source PRs."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from build_business_pilot_audience_preview import MANIFEST, digest, require, write_preview
from prepare_phuket_universe_static_r1 import file_index, payload_digest
from rehearse_pilot_audience_release import CANDIDATE, JOINT_MANIFEST, PUBLISHED, ROOT, snapshot
from restored_guides_release import manifest_bytes
from test_pilot_snapshot_routes import test_snapshot

EXERCISE_COMMIT = "0c87e0795f8e898ef06bacd4840579a1af5dac7b"
CARD_COMMIT = "5ca166f7a905c6887ae872fc6931b71ca76ac17a"
PAGE = "guides/ai-first-tasks-for-adults.html"
EXERCISE = "docs/release-candidates/meeting-notes-r1-20261123/prepare.py"


def checkout(destination: Path, commit: str) -> None:
    subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(destination)], check=True)
    subprocess.run(["git", "checkout", "--quiet", "--detach", commit], cwd=destination, check=True)


def build_joint(r4: Path, output: Path) -> None:
    files = snapshot(r4, CANDIDATE)
    with TemporaryDirectory(prefix="pilot-articles-") as tmp:
        work = Path(tmp)
        exercise = work / "exercise"
        checkout(exercise, EXERCISE_COMMIT)
        patch = subprocess.check_output([sys.executable, "-B", EXERCISE], cwd=exercise)
        subprocess.run(["git", "apply", "-"], input=patch, cwd=exercise, check=True)
        for name in (PAGE, "en/" + PAGE):
            files[name] = (exercise / "deploy/live" / name).read_bytes()
        card = work / "card"
        checkout(card, CARD_COMMIT)
        files[PAGE] = subprocess.check_output(
            [sys.executable, "-B", "-c",
             "import sys; from stage_first_tasks_card import update_card; "
             "sys.stdout.buffer.write(update_card(sys.stdin.buffer.read()))"],
            input=files[PAGE], cwd=card / "scripts")

    rows = file_index(files)
    payload = payload_digest(rows)
    release = "AISL_ADULT_GUIDE_AND_BUSINESS_PILOT_R4_REVIEW_1_" + payload
    manifest = {"schema": "ai-skill-lab.static-release.v1", "files": rows, "file_count": len(rows),
                "release_id": release, "patch_id": release, "parent_manifest_sha256": PUBLISHED,
                "payload_sha256": payload}
    files[MANIFEST] = manifest_bytes(manifest)
    require(digest(files[MANIFEST]) == JOINT_MANIFEST, "joint review package does not match")
    write_preview(output, files)
    test_snapshot(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("r4", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build_joint(args.r4.resolve(), args.output.resolve())
