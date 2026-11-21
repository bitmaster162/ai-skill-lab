"""Check localized safety links, unchanged policy and exact replay of the preceding release."""
from html.parser import HTMLParser
import subprocess
import sys
import xml.etree.ElementTree as ET

import certificate_donor_release as release
from diagnostic_intent_release import historical_workspace


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.append(dict(attrs).get("href"))


def rejects(reason, **inputs):
    try:
        release.verify(**inputs)
    except ValueError as exc:
        assert reason in str(exc), str(exc)
    else:
        raise AssertionError("Accepted a corrupted candidate: " + reason)


manifest = release.verify()
assert manifest["file_count"] == 112
rejects("manifest digest", manifest_override=(release.LIVE / "_release.json").read_bytes() + b" ")
for page, (source, href, label, _, _) in release.LINKS.items():
    html = (release.LIVE / page).read_bytes()
    links = Anchors()
    links.feed(html.decode())
    assert links.hrefs.count(href) == 1 and (release.LIVE / (href.lstrip("/") + ".html")).is_file()
    other = "/certificate" if page.startswith("en/") else "/en/certificate"
    rejects("static " + page, file_overrides={page: html.replace(f'href="{href}"'.encode(),
                                                                f'href="{other}"'.encode())})
    visible = ("<u>" + label + "</u>").encode()
    assert html.count(visible) == 1
    rejects("static " + page, file_overrides={page: html.replace(visible, label.encode())})
    assert html.count(b'data-policy-verified="2026-10-29"') == 1
    rejects("static " + page, file_overrides={page: html.replace(b"2026-10-29", b"2026-11-22", 1)})
    rejects("source " + source, source_overrides={source: release.original(source)})
before_xml = release.original("deploy/live/sitemap.xml")
xml = (release.LIVE / "sitemap.xml").read_bytes()
def dates(raw):
    return {item.findtext("{*}loc"): item.findtext("{*}lastmod")
            for item in ET.fromstring(raw).findall("{*}url")}
old, new = dates(before_xml), dates(xml)
assert len(old) == 56 and old.keys() == new.keys()
assert {url for url in new if old[url] != new[url]} == {
    "https://aiskillab.work/safety", "https://aiskillab.work/en/safety"}
rejects("static sitemap.xml", file_overrides={"sitemap.xml": before_xml})
for rel in ("app/sitemap.ts", "lib/guides.ts"):
    rejects("source " + rel, source_overrides={rel: release.original(rel)})
rejects("static byte certificate.html", file_overrides={"certificate.html": b"changed"})
rejects("unknown file", file_overrides={"elsewhere": b""})
# Execute the earlier release's unmodified tests on the exact files they admitted.
with historical_workspace(release.PARENT_COMMIT, ["deploy/live", "scripts", *release.previous.SOURCE_SHA]) as root:
    subprocess.run([sys.executable, "-B", "scripts/test_sitemap_route_dates_release.py"], cwd=root, check=True)
print("Certificate links verified: 2 localized donors, 2 sitemap dates, 109 preserved assets.")
