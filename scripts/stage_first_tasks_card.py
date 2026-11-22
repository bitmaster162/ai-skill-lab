"""Build a reproducible preview ZIP without touching either sealed deploy/live tree."""

import argparse
import io
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import zipfile

from build_guides import ROOT, apply_card_metadata
from build_release_artifacts import deterministic_zip, sha256
from restored_guides_release import manifest_bytes

ROUTE = "/guides/ai-first-tasks-for-adults"
PAGE = ROUTE[1:] + ".html"
PARENTS = {
    "restored": (
        "2444bd77f7616ba916c37b2b3bcba11898926be0",
        "66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5",
        "AISL_FIRST_TASKS_CARD_R1_20261122",
        "f9c1772529afcbbdcc82ef3c10aa8252000a7e49a3d8f212af4f39f91de89cfc",
    ),
    "matcher": (
        "f4301e72991e83a36e11a4a2f27c1cf5f2e65cef",
        "d4de99d99f7542afb5e853fecfbcc85674ac6dcd07d5c10d3c72154e20268329",
        "AISL_MATCHER_FIRST_TASKS_CARD_R1_20261122",
        "588a6597d659c15b5e8e05e4f0d9796417b8961e4010698e17e7976dab77e3b3",
    ),
}
# A change to the reviewed card or its text requires a new release identity.
PAGE_SHA = "c11fd355535a82fc8f58e4b6ccd553520e1671366f10e5ddc77dac46cc1820e2"


def update_card(page):
    head, body = page.decode("utf-8").split("</head>", 1)
    head = apply_card_metadata(head, ROUTE, "AI Skill Lab · Phuket")
    return (head + "</head>" + body).encode("utf-8")


def candidate(parent):
    commit, parent_digest, release_id, expected_digest = PARENTS[parent]
    archive = subprocess.check_output(
        ["git", "archive", "--format=zip", commit + ":deploy/live"], cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        files = {entry.filename: source.read(entry) for entry in source.infolist() if not entry.is_dir()}
    raw = files.pop("_release.json")
    if sha256(raw) != parent_digest:
        raise ValueError("Parent manifest digest mismatch")
    manifest = json.loads(raw)
    rows = manifest["files"]
    if {row["path"] for row in rows} != set(files) or len(rows) != manifest["file_count"]:
        raise ValueError("Parent inventory mismatch")
    for row in rows:
        raw = files[row["path"]]
        if len(raw) != row["size"] or sha256(raw) != row["sha256"]:
            raise ValueError("Parent asset mismatch: " + row["path"])
    files[PAGE] = update_card(files[PAGE])
    if sha256(files[PAGE]) != PAGE_SHA:
        raise ValueError("Card changed since this release was sealed")
    target, = (row for row in rows if row["path"] == PAGE)
    target.update(size=len(files[PAGE]), sha256=PAGE_SHA)
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in rows)
    manifest.update(release_id=release_id, patch_id=release_id, parent_manifest_sha256=parent_digest,
                    payload_sha256=sha256(listing.encode()))
    files["_release.json"] = manifest_bytes(manifest)
    if sha256(files["_release.json"]) != expected_digest:
        raise ValueError("Successor manifest digest mismatch")
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", choices=PARENTS, required=True,
                        help="Matcher requires the exact reviewed PR 253 commit in local Git history.")
    parser.add_argument("--output", type=Path, required=True, help="New ZIP file outside the checkout.")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT.resolve()):
        parser.error("Choose a destination outside the checkout.")
    files = candidate(args.parent)
    with TemporaryDirectory(dir=output.parent) as temp:
        staged = Path(temp) / "candidate.zip"
        deterministic_zip(staged, files)
        checksum = sha256(staged.read_bytes())
        os.link(staged, output)  # Atomic, including simultaneous runs. No overwrite.
    print(f"{checksum}  {output.name}")


if __name__ == "__main__":
    main()
