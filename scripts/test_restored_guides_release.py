"""Prove the four restored routes, their bilingual navigation, and their release boundaries."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

import restored_guides_release as release
from diagnostic_intent_release import historical_workspace


class Page(HTMLParser):
    def __init__(self, raw):
        super().__init__()
        self.lang = None
        self.canonical = []
        self.alternates = {}
        self.heading_count = 0
        self.links = []
        self.ids = set()
        self.scripts = []
        self.feed(raw.decode())

    def handle_starttag(self, name, attrs):
        d = dict(attrs)
        if name == "html":
            self.lang = d.get("lang")
        if name == "h1":
            self.heading_count += 1
        if "id" in d:
            self.ids.add(d["id"])
        if name == "a" and "href" in d:
            self.links.append(d["href"])
        if name == "script" and "src" in d:
            self.scripts.append(d["src"])
        if name == "link" and d.get("rel") == "canonical":
            self.canonical.append(d["href"])
        if name == "link" and d.get("rel") == "alternate" and "hreflang" in d:
            self.alternates[d["hreflang"]] = d["href"]


def dates(raw):
    rows = ET.fromstring(raw).findall("{*}url")
    parsed = {urlsplit(row.findtext("{*}loc")).path: row.findtext("{*}lastmod") for row in rows}
    assert len(parsed) == len(rows)
    return parsed


def rejects(origin, mutate):
    with TemporaryDirectory() as tmp:
        live = Path(tmp) / "live"
        shutil.copytree(origin, live)
        mutate(live)
        with patch.object(release, "LIVE", live):
            try:
                release.verify()
            except ValueError:
                return
        raise AssertionError("Tampered fixture was accepted")


release.verify()
before = dates(release.original("deploy/live/sitemap.xml"))
after = dates((release.LIVE / "sitemap.xml").read_bytes())
assert len(before) == 56 and len(after) == 60
assert after.keys() - before.keys() == release.NEW_ROUTES and before.keys() <= after.keys()
assert {r for r, date in before.items() if after[r] != date} == {"/guides", "/en/guides"}
assert all(after[r] == release.DATE for r in release.NEW_ROUTES | {"/guides", "/en/guides"})

for route in sorted(release.NEW_ROUTES):
    translated = route.removeprefix("/en") if route.startswith("/en/") else "/en" + route
    lang = "en" if route.startswith("/en/") else "ru"
    prefix = "/en" if lang == "en" else ""
    page = Page((release.LIVE / (route[1:] + ".html")).read_bytes())
    assert page.lang == lang and page.heading_count == 1
    assert page.canonical == [release.ORIGIN + route]
    assert page.alternates[lang] == release.ORIGIN + route
    assert page.alternates["ru" if lang == "en" else "en"] == release.ORIGIN + translated
    assert translated in page.links and prefix + "/start#application-form" in page.links
    assert all("analytics/" not in src for src in page.scripts)
    catalog = Page((release.LIVE / (prefix[1:] + "/" if prefix else "") / "guides.html").read_bytes())
    assert route in catalog.links
    for href in page.links:
        destination = urlsplit(href)
        if destination.netloc not in ("", "aiskillab.work") or destination.scheme not in ("", "https"):
            continue
        path = destination.path or route
        assert path in after, (route, path)
        if destination.fragment:
            relative = "index.html" if path == "/" else path[1:] + ".html"
            target = Page((release.LIVE / relative).read_bytes())
            assert destination.fragment in target.ids, (route, href)

for name in ("guides/ai-start-for-adults.html", "en/guides/ai-pilot-for-small-business.html",
             "sitemap.xml", "vercel.json", "lead-form-runtime.js"):
    rejects(release.LIVE, lambda live, rel=name: (live / rel).write_bytes(b"changed"))
rejects(release.LIVE, lambda live: (live / "_release.json").write_bytes(release.original("deploy/live/_release.json")))
rejects(release.LIVE, lambda live: (live / "unexpected.html").write_bytes(b""))
with TemporaryDirectory() as tmp:
    root = Path(tmp)
    source = "guides/aiskillab/ai-start-for-adults.en.md"
    fake = root / source
    fake.parent.mkdir(parents=True)
    fake.write_bytes(b"unreviewed content")
    with patch.object(release, "ROOT", root):
        try:
            release.source_sha(source)
        except ValueError:
            pass
        else:
            raise AssertionError("Unreviewed guide source was accepted")
with historical_workspace(release.PARENT_COMMIT, ["deploy/live", "scripts", "components", "lib", "app", "public", "guides"]) as parent:
    subprocess.run([sys.executable, "-B", "scripts/test_universe_en_home_release.py"], cwd=parent, check=True)
print("Verified 60 routes, four restored articles, exact release and negative fixtures; replayed archived #251.")
