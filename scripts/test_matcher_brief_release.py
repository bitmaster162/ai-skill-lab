"""Verify the one-file delta and replay the sealed #252 guide fixtures."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

from diagnostic_intent_release import historical_workspace
import matcher_brief_release as release


current = release.verify()
parent = json.loads(release.original("deploy/live/_release.json"))
previous = {row["path"]: row for row in parent["files"]}
assert len(current["files"]) == len(previous) == 116
assert {r["path"] for r in current["files"] if previous[r["path"]] != r} == {"matcher-v2.js"}

with TemporaryDirectory() as tmp:
    live = Path(tmp) / "live"
    shutil.copytree(release.LIVE, live)
    with patch.object(release, "LIVE", live):
        for name, replacement in (
                ("matcher-v2.js", release.original("deploy/live/matcher-v2.js")),
                ("guides/ai-start-for-adults.html", b"changed article"),
                ("_release.json", release.original("deploy/live/_release.json"))):
            path = live / name
            original = path.read_bytes()
            path.write_bytes(replacement)
            try:
                release.verify()
            except ValueError:
                pass
            else:
                raise AssertionError("Tampered release admitted: " + name)
            path.write_bytes(original)

files = ["deploy/live", "scripts", "components", "lib", "app", "public", "guides", "README.md"]
with historical_workspace(release.PARENT_COMMIT, files) as parent_root:
    subprocess.run([sys.executable, "-B", "scripts/test_restored_guides_release.py"],
                   cwd=parent_root, check=True)
print("Verified matcher-only successor, 116 assets, tamper fixtures and the #252 guide replay.")
