"""Check the two social cards, tamper rejection and the unchanged historical release."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from check_og20_r1 import MetaParser, png_dimensions
from diagnostic_intent_release import historical_workspace
import ru_guide_cards_release as release


checks = TestCase()
current = release.verify()
checks.assertEqual(current["file_count"], 116)
cards = json.loads((release.ROOT / "guides/aiskillab/social-cards.json").read_bytes())
replaceable = re.compile(rb'<meta (?:property|name)="(?:og|twitter):image(?::alt)?" content="[^"]*">')
checks.assertEqual({route[1:] + ".html" for route in cards}, release.CHANGED)
for route, card in cards.items():
    rel = route[1:] + ".html"
    article = (release.LIVE / rel).read_bytes()
    historical = release.original("deploy/live/" + rel)
    # The archived pages lacked Twitter image alt text. Strip only these tags to compare all other bytes.
    new_page, new_count = replaceable.subn(b"", article)
    old_page, old_count = replaceable.subn(b"", historical)
    checks.assertEqual((new_count, old_count), (4, 3))
    checks.assertTrue(new_page == old_page, "Unrelated page bytes changed: " + route)
    parsed = MetaParser()
    parsed.feed(article.decode("utf-8"))
    for prefix in ("og", "twitter"):
        checks.assertEqual(parsed.meta[prefix + ":image"], "https://aiskillab.work" + card["url"])
        checks.assertEqual(parsed.meta[prefix + ":image:alt"], card["alt"])
    checks.assertEqual(png_dimensions((release.LIVE / card["url"][1:]).read_bytes()), (1200, 630))

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    live = root / "live"
    shutil.copytree(release.LIVE, live)
    with patch.object(release, "LIVE", live):
        for rel in (*sorted(release.CHANGED), "_release.json"):
            path = live / rel
            original = path.read_bytes()
            path.write_bytes(release.original("deploy/live/" + rel))
            with checks.assertRaisesRegex(ValueError, re.escape("static " + rel)):
                release.verify()
            path.write_bytes(original)
        unchanged = live / "og-ru-personal.png"
        copy = root / "card-copy.png"
        unchanged.rename(copy)
        with checks.assertRaisesRegex(ValueError, "missing asset"):
            release.verify()
        unchanged.symlink_to(copy)
        with checks.assertRaisesRegex(ValueError, "filesystem entry"):
            release.verify()
        unchanged.unlink()
        copy.rename(unchanged)
        original_image = unchanged.read_bytes()
        unchanged.write_bytes(original_image[:-1] + bytes([original_image[-1] ^ 1]))
        with checks.assertRaisesRegex(ValueError, "static og-ru-personal.png"):
            release.verify()
        unchanged.write_bytes(original_image)
        (live / "unscheduled.html").write_text("extra", encoding="utf-8")
        with checks.assertRaisesRegex(ValueError, "unexpected or missing asset"):
            release.verify()
    rel = "guides/aiskillab/social-cards.json"
    source = root / rel
    source.parent.mkdir(parents=True)
    source.write_text("{}", encoding="utf-8")
    with patch.object(release, "ROOT", root), checks.assertRaisesRegex(ValueError, "source"):
        release.source_sha(rel)

files = ["deploy/live", "scripts", "components", "lib", "app", "public", "guides", "README.md"]
with historical_workspace(release.PARENT_COMMIT, files) as parent:
    subprocess.run([sys.executable, "-B", "scripts/test_restored_guides_release.py"], cwd=parent, check=True)
print("Verified two Russian social cards, all 116 assets, negative fixtures and the archived #252 release.")
