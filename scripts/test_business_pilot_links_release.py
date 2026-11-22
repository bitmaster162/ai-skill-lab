"""Verify the current release, both donor clicks, inherited cards, and exact failure cases."""
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

import business_pilot_links_release as release
from diagnostic_intent_release import historical_workspace

check = TestCase()


class PilotSection(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = []
        self.links = []
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if tag == "section":
            self.sections.append({"text": "", "links": [], "steps": 0})
        elif self.sections and tag == "article":
            self.sections[-1]["steps"] += 1
        elif self.sections and tag == "a":
            self.current_link = [props.get("href"), ""]
            self.sections[-1]["links"].append(self.current_link)

    def handle_data(self, data):
        if self.sections:
            self.sections[-1]["text"] += data
        if self.current_link is not None:
            self.current_link[1] += data

    def handle_endtag(self, tag):
        if tag == "section" and self.sections:
            self.links.append(self.sections.pop())
        if tag == "a":
            self.current_link = None


def test_release():
    manifest = release.verify()
    check.assertEqual(manifest["file_count"], 116)
    parent = release.cards.expected_files()
    current = release.expected_files()
    check.assertEqual({p for p in current if current[p] != parent[p]}, release.CHANGED | {"_release.json"})
    for rel, (url, label) in release.LINKS.items():
        parsed = PilotSection()
        parsed.feed(current[rel].decode("utf-8"))
        sections = [s for s in parsed.links if [url, label] in s["links"]]
        check.assertEqual(len(sections), 1)
        pilot, = sections
        check.assertEqual(pilot["steps"], 4)
        check.assertIn("IMPLEMENTATION PILOT" if rel.startswith("en/") else "ВНЕДРЕНИЕ ПИЛОТА", pilot["text"])
        check.assertEqual(pilot["links"], [[url, label]])
        check.assertIn(f'href="https://aiskillab.work{url}"'.encode(), current[url[1:] + ".html"])
    def whatsapp(page):
        href, = re.findall(rb'href="(https://wa[.]me/66649701204[?]text=[^"]+)"', page)
        return href.decode("utf-8")
    # Compare complete WHATWG href serialization, including the original message.
    contact_check = "const [a,b] = process.argv.slice(1); if (new URL(a).href !== new URL(b).href) process.exit(1)"
    subprocess.run(["node", "-e", contact_check, whatsapp(current["business.html"]),
                    whatsapp(parent["business.html"])], check=True)
    with TemporaryDirectory() as tmp:
        live = Path(tmp) / "site"
        shutil.copytree(release.LIVE, live)
        with patch.object(release, "LIVE", live):
            for rel in sorted(release.CHANGED | {"_release.json"}):
                path = live / rel
                path.write_bytes(parent[rel])
                with check.assertRaisesRegex(ValueError, re.escape("static " + rel)):
                    release.verify()
                path.write_bytes(current[rel])
            path = live / "og-ru-business.png"
            path.write_bytes(path.read_bytes()[:-1])
            with check.assertRaisesRegex(ValueError, "static og-ru-business.png"):
                release.verify()
            path.write_bytes(current["og-ru-business.png"])
            (live / "extra.html").write_bytes(b"")
            with check.assertRaisesRegex(ValueError, "unexpected or missing"):
                release.verify()
        component = Path(tmp) / release.COMPONENT
        component.parent.mkdir(parents=True)
        component.write_bytes(b"")
        with patch.object(release, "ROOT", Path(tmp)), check.assertRaisesRegex(ValueError, "component"):
            release.source_sha(release.COMPONENT)
    # Run the parent's unchanged regression tests in its own exact tree.
    files = ["deploy/live", "scripts", "components", "lib", "app", "public", "guides", "README.md"]
    with historical_workspace(release.PARENT_COMMIT, files) as root:
        subprocess.run([sys.executable, "-B", "scripts/test_ru_guide_cards_release.py"], cwd=root, check=True)
    print("Verified 116 assets, both pilot links, historical card tests and tamper rejection.")


if __name__ == "__main__":
    if release.active():
        test_release()
    else:
        # The parent verifier must independently recognize any alternate manifest.
        subprocess.run([sys.executable, "-B", "scripts/test_ru_guide_cards_release.py"], cwd=release.ROOT, check=True)

