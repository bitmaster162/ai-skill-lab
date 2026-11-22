"""Check the two localized home links, the one changed date and the original release."""
from html.parser import HTMLParser
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

import universe_en_home_release as release
from diagnostic_intent_release import historical_workspace


class HeaderLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_nav = False
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "nav":
            self.in_nav = attrs.get("class") == "pu-s009"
        if tag == "a" and self.in_nav:
            self.urls.append(attrs["href"])

    def handle_endtag(self, tag):
        if tag == "nav":
            self.in_nav = False


def header_links(markup):
    parser = HeaderLinks()
    parser.feed(markup)
    return parser.urls


def dates(data):
    return {r.findtext("{*}loc"): r.findtext("{*}lastmod") for r in ET.fromstring(data).findall("{*}url")}


def rejects(reason, **inputs):
    try:
        release.verify(**inputs)
    except ValueError as exc:
        assert reason in str(exc), str(exc)
    else:
        raise AssertionError("Admitted " + reason)


release.verify()
source = (release.ROOT / "components/phuketUniverseMarkup.ts").read_text(encoding="utf-8")
markup = json.loads(source.split("export const phuketUniverseMarkup = ", 1)[1].rsplit(" as const;", 1)[0])
for locale, page, origin, counterpart in (
    ("ru", "phuket-universe.html", "https://aiskillab.work", "/en/phuket-universe"),
    ("en", "en/phuket-universe.html", "/en", "/phuket-universe"),
):
    expected = ["#orbit", "#homes", "#agencies", origin, counterpart]
    assert header_links(markup[locale]) == expected
    assert header_links((release.LIVE / page).read_text(encoding="utf-8")) == expected
old = dates(release.original("deploy/live/sitemap.xml"))
new = dates((release.LIVE / "sitemap.xml").read_bytes())
assert new.keys() == old.keys() and len(new) == 56
assert {u for u in new if new[u] != old[u]} == {"https://aiskillab.work/en/phuket-universe"}
assert new["https://aiskillab.work/en/phuket-universe"] == release.DATE
for page in release.CHANGED:
    rejects("static " + page, file_overrides={page: release.original("deploy/live/" + page)})
for path in release.SOURCE_SHA:
    rejects("source " + path, source_overrides={path: release.original(path)})
rejects("manifest digest", manifest_override=release.original("deploy/live/_release.json"))
rejects("unknown file", file_overrides={"unused-route.html": b""})

# Replay the archived test using exactly the source, static tree and fixtures from #250.
with historical_workspace(release.PARENT_COMMIT, ["deploy/live", "scripts", "components", "lib", "app", "public"]) as root:
    subprocess.run([sys.executable, "-B", "scripts/test_telegram_card_release.py"], cwd=root, check=True)
print("Verified localized home links on both routes, one changed sitemap date, and archived #250 tests.")
